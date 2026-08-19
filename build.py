"""Build pipeline de Santy POS para Vercel.

Ejecutado por el Build Command de Vercel (ver vercel.json):
1. Compila Tailwind CSS (npm ci + build) -> static/css/output.css.
2. Recopila estáticos (Vercel los sirve por CDN).
3. Aplica migraciones solo en deploy de producción (VERCEL_ENV=production).
"""

import os
import subprocess

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "santy.settings")

import django  # noqa: E402

django.setup()

from django.core.management import call_command  # noqa: E402


def _npm() -> str:
    """Nombre del binario de npm según la plataforma."""
    return "npm.cmd" if os.name == "nt" else "npm"


def main() -> None:
    print("-> Construyendo Tailwind CSS")
    subprocess.run([_npm(), "ci"], check=True)
    subprocess.run([_npm(), "run", "build"], check=True)

    print("-> Recopilando estáticos")
    call_command("collectstatic", interactive=False)

    if os.environ.get("VERCEL_ENV") == "production":
        print("-> Aplicando migraciones (producción)")
        call_command("migrate", interactive=False, noinput=True)
    else:
        print(f"-> VERCEL_ENV={os.environ.get('VERCEL_ENV')!r}; omitiendo migrate")

    print("-> Build completado")


if __name__ == "__main__":
    main()