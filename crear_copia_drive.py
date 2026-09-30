"""Genera la copia de seguridad del proyecto y la sincroniza con Google Drive.

La copia local siempre se genera en la carpeta del proyecto. Si Google Drive
para escritorio tiene disponible la carpeta 'Copias de seguridad Dashboard',
el ZIP se copia allí con el mismo nombre para que Drive lo sincronice.
"""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import os
import shutil
import sys

ROOT = Path(__file__).resolve().parent
ARCHIVE_NAME = "COPIA_SEGURIDAD_DASHBOARD.zip"
LOCAL_ARCHIVE = ROOT / ARCHIVE_NAME
DRIVE_FOLDER_NAME = "Copias de seguridad Dashboard"


def find_drive_folder():
    """Busca la carpeta local habitual de Google Drive para escritorio."""
    candidates = []

    # Permite indicar una ruta personalizada sin editar el script.
    configured = os.environ.get("ECO_DRIVE_BACKUP", "").strip()
    if configured:
        candidates.append(Path(configured))

    home = Path.home()
    drive_names = ("Mi unidad", "My Drive", "Google Drive")
    for drive_name in drive_names:
        candidates.extend([
            home / drive_name / DRIVE_FOLDER_NAME,
            Path(f"G:/{drive_name}") / DRIVE_FOLDER_NAME,
            Path(f"C:/{drive_name}") / DRIVE_FOLDER_NAME,
        ])

    # Algunas instalaciones de Drive for Desktop dejan la carpeta en otra
    # unidad; se comprueban las unidades montadas sin modificar nada.
    for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
        for drive_name in drive_names:
            candidates.append(Path(f"{letter}:/{drive_name}") / DRIVE_FOLDER_NAME)

    seen = set()
    for folder in candidates:
        key = str(folder).lower()
        if key in seen:
            continue
        seen.add(key)
        if folder.is_dir():
            return folder
    return None


def make_archive():
    """Crea el ZIP sin incluir el ZIP ni carpetas temporales del sistema."""
    file_count = 0
    # No se usan rglob porque seguiría descendiendo en carpetas temporales
    # grandes. Excluir .tmp.driveupload evita incluir el propio staging de
    # Google Drive y que la copia crezca de forma recursiva.
    excluded_dirs = {
        ".tmp.driveupload",
        ".tmp.drivedownload",
        "__pycache__",
        ".git",
        ".freebuff",
    }
    with ZipFile(LOCAL_ARCHIVE, "w", ZIP_DEFLATED, compresslevel=6) as archive:
        for current_dir, dirnames, filenames in os.walk(ROOT, followlinks=False):
            current = Path(current_dir)
            dirnames[:] = [d for d in dirnames if d not in excluded_dirs]
            for filename in filenames:
                path = current / filename
                if path == LOCAL_ARCHIVE or not path.is_file():
                    continue
                archive.write(path, path.relative_to(ROOT).as_posix())
                file_count += 1
    return file_count


def copy_to_drive(folder):
    """Sustituye el ZIP de Drive mediante un temporal para evitar partly-written files."""
    destination = folder / ARCHIVE_NAME
    temporary = folder / (ARCHIVE_NAME + ".tmp")
    shutil.copy2(LOCAL_ARCHIVE, temporary)
    os.replace(temporary, destination)
    return destination


# La carpeta de Drive guarda un archivo que recuerda de qué carpeta del proyecto
# se generó el ZIP. Así, si alguien ejecuta actualizar.bat desde una COPIA del
# proyecto (una prueba, otra carpeta...), no pisa la copia de seguridad real.
ORIGEN_NAME = "origen.txt"


def es_el_proyecto_que_gestiona_drive(folder):
    """True si esta carpeta es la proprietaria de la copia de Drive.

    La primera vez no hay archivo de origen, asi que esta carpeta queda
    registrada como la buena. Si ya existe y es otra, no se toca la copia.
    """
    origen = folder / ORIGEN_NAME
    actual = str(ROOT)
    if not origen.exists():
        try:
            origen.write_text(actual, encoding="utf-8")
        except OSError:
            pass
        return True
    try:
        registrado = origen.read_text(encoding="utf-8").strip()
    except OSError:
        return True
    if registrado and registrado.lower() != actual.lower():
        return False
    return True


def main():
    if not ROOT.is_dir():
        print("ERROR: No se encontró la carpeta del proyecto.", file=sys.stderr)
        return 1

    try:
        file_count = make_archive()
        print(f"OK: Copia local creada: {LOCAL_ARCHIVE}")
        print(f"Archivos incluidos: {file_count}")
        print(f"Tamaño: {LOCAL_ARCHIVE.stat().st_size:,} bytes")

        drive_folder = find_drive_folder()
        if drive_folder is None:
            print()
            print("AVISO: No se encontró la carpeta local de Google Drive.")
            print("La copia local está creada igualmente.")
            print("Para sincronizarla automáticamente:")
            print("  1. Instala y abre Google Drive para escritorio.")
            print("  2. Inicia sesión con tu cuenta.")
            print("  3. Abre la carpeta 'Copias de seguridad Dashboard' en el ordenador.")
            print("  4. Ejecuta de nuevo actualizar.bat.")
            return 0

        if not es_el_proyecto_que_gestiona_drive(drive_folder):
            registrado = (drive_folder / ORIGEN_NAME).read_text(encoding="utf-8").strip()
            print()
            print("AVISO: esta carpeta NO es la del proyecto que gestiona la copia de Drive.")
            print(f"       La copia de Drive pertenece a: {registrado}")
            print(f"       Aqui solo se ha creado la copia local: {LOCAL_ARCHIVE}")
            print("       No se ha tocado la copia de Drive para no pisarla.")
            return 0

        try:
            destination = copy_to_drive(drive_folder)
        except (OSError, PermissionError) as exc:
            print()
            print(f"AVISO: Se creó la copia local, pero no se pudo copiar a Drive: {exc}")
            print(f"Carpeta detectada: {drive_folder}")
            return 1

        print()
        print("OK: Copia sincronizada con Google Drive para escritorio.")
        print(f"Destino: {destination}")
        print("Google Drive subirá o reemplazará el ZIP automáticamente.")
        return 0
    except (OSError, PermissionError, ValueError) as exc:
        print(f"ERROR: No se pudo crear la copia de seguridad: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
