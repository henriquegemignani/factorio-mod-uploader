# factorio-mod-uploader
GitHub workflow action for uploading Factorio mod packages to the mod portal


# Usage

```yaml

jobs:
  package:
    runs-on: ubuntu-latest
    outputs:
      name: ${{ steps.package_details.outputs.name }}
      version: ${{ steps.package_details.outputs.version }}

    steps:
      - name: Check out repository code
        uses: actions/checkout@v4

      - name: Get Package details
        id: package_details
        shell: bash
        run: |
          echo "name=$(jq -r .name info.json)" >> $GITHUB_OUTPUT
          echo "version=$(jq -r .version info.json)" >> $GITHUB_OUTPUT

      - name: Create Package
        shell: bash
        run: |
          mkdir -p build
          tar c \
            --transform 's|./|${{ steps.package_details.outputs.name }}-${{ steps.package_details.outputs.version }}/|' \
            --exclude '.git' --exclude '.github' --exclude 'dist' --exclude 'build' \
            --exclude 'tools' \
            . | tar x -C build/
          
          mkdir -p dist
          (
            cd build; zip -r \
              ../dist/${{ steps.package_details.outputs.name }}-${{ steps.package_details.outputs.version }}.zip \
              ${{ steps.package_details.outputs.name }}-${{ steps.package_details.outputs.version }}/
          )

      - name: Upload artifact
        uses: actions/upload-artifact@v4.0.0
        with:
          name: Package
          if-no-files-found: error
          path: dist/

  release-modportal:
    runs-on: ubuntu-latest
    needs: [package]
    if: startsWith(github.ref, 'refs/tags/')
    steps:
      - name: Download the executable
        uses: actions/download-artifact@v4
        with:
          name: Package
          path: dist/

      - name: Factorio release
        uses: henriquegemignani/factorio-mod-uploader@v1
        with:
          zip_file: "dist/${{ needs.package.outputs.name }}-${{ needs.package.outputs.version }}.zip"
          api_key: "${{ secrets.FACTORIO_API_KEY }}"
```