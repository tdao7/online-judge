#!/bin/sh
# ============================================================================
# DMOJ SCSS Build Pipeline — VCODER Design System
# ============================================================================

set -e

if ! [ -x "$(command -v sass)" ]; then
  echo 'Error: sass is not installed. Please install Dart Sass.' >&2
  exit 1
fi

HAS_POSTCSS=false
if [ -x "$(command -v postcss)" ] && [ -x "$(command -v autoprefixer)" ]; then
  HAS_POSTCSS=true
else
  echo 'Notice: postcss or autoprefixer not found in PATH; compiling via direct Dart Sass.'
fi

cd "$(dirname "$0")" || exit

build_style() {
  THEME_NAME="$1"
  TARGET_DIR="$2"

  echo "=========================================="
  echo "Building $THEME_NAME style -> $TARGET_DIR..."
  echo "=========================================="

  # Always clean sass_processed directory to prevent leftover trailing bytes from previous builds
  rm -rf sass_processed
  mkdir -p "$TARGET_DIR"

  # Link or copy theme vars file to active vars.scss
  cp "resources/vars-$THEME_NAME.scss" resources/vars.scss

  # Run Dart Sass compiler on resources directory
  sass resources:sass_processed

  if [ "$HAS_POSTCSS" = true ]; then
    echo "Running PostCSS with Autoprefixer..."
    postcss \
        sass_processed/ace-dmoj.css \
        sass_processed/featherlight.css \
        sass_processed/martor-description.css \
        sass_processed/select2-dmoj.css \
        sass_processed/style.css \
        sass_processed/problems-list.css \
        sass_processed/problem-workspace.css \
        sass_processed/submissions-list.css \
        sass_processed/submission-drawer.css \
        --verbose --use autoprefixer -d "$TARGET_DIR"
  else
    echo "Copying compiled CSS directly to $TARGET_DIR..."
    cp sass_processed/ace-dmoj.css \
       sass_processed/featherlight.css \
       sass_processed/martor-description.css \
       sass_processed/select2-dmoj.css \
       sass_processed/style.css \
       sass_processed/problems-list.css \
       sass_processed/problem-workspace.css \
       sass_processed/submissions-list.css \
       sass_processed/submission-drawer.css \
       "$TARGET_DIR/"
  fi

  # Cleanup temporary working files
  rm -f resources/vars.scss
  rm -rf sass_processed
  echo "Successfully built $THEME_NAME style!"
}

# Mode selection: allow passing theme as argument or default to vcoder + dark
TARGET_THEME="${1:-all}"

case "$TARGET_THEME" in
  vcoder)
    build_style 'vcoder' 'resources'
    ;;
  default)
    build_style 'default' 'resources'
    ;;
  dark)
    build_style 'dark' 'resources/dark'
    ;;
  all)
    build_style 'vcoder' 'resources'
    build_style 'dark' 'resources/dark'
    ;;
  *)
    echo "Usage: $0 [vcoder|default|dark|all]"
    exit 1
    ;;
esac
