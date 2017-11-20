prefix 		= /usr/local
BIN_DIR   = $(prefix)/bin
LIB_DIR   = $(prefix)/lib
APP_DIR 	= $(LIB_DIR)/gostp
LOADER    = gostp

all:
	@echo "usage: make [install|uninstall]"

test:
	make install && make uninstall

install:
	gem list | grep "^fastlane " || sudo gem install fastlane
	brew list apng2gif &>/dev/null || brew install apng2gif
	brew list ffmpeg &>/dev/null || brew install ffmpeg
	brew list apngasm &>/dev/null || brew install apngasm

	git clone https://github.com/metasmile/git-xcp.git $(CURDIR)/git-xcp && \
	cd $(CURDIR)/git-xcp && \
	make install >/dev/null 2>&1 && \
	cd $(CURDIR) && \
	rm -rf $(CURDIR)/git-xcp

	rsync -av --exclude=".git*" --delete $(CURDIR) $(LIB_DIR)
	chmod -R +r $(APP_DIR)
	chmod +x $(APP_DIR)/$(LOADER)

	ln -fs $(APP_DIR)/$(LOADER) $(BIN_DIR)

uninstall:
	rm -rf $(APP_DIR)
	unlink $(BIN_DIR)/$(LOADER)
