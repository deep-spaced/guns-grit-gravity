.PHONY: install build dev preview clean

# Install npm dependencies
install:
	npm install

# Build Svelte app into dist/
build:
	npm run build

# Vite dev server with hot reload
dev:
	npm run dev

# Preview production build locally
preview:
	npm run preview

# Remove build artifacts
clean:
	rm -rf dist node_modules/.vite
