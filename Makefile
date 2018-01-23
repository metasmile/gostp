prefix 		= /usr/local
BIN_DIR   = $(prefix)/bin
# LIB_DIR   = $(prefix)/lib
# APP_DIR 	= $(LIB_DIR)/gostp
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

	rsync -av --exclude=".git*" --delete $(CURDIR)/* $(BIN_DIR)
	# chmod -R +r $(APP_DIR)
	# chmod +x $(APP_DIR)/$(LOADER)
	# ln -fs $(APP_DIR)/$(LOADER) $(BIN_DIR)
	# @$(foreach cmd,$(COMMANDS),ln -fs $(APP_DIR)/$(cmd) $(BIN_DIR);)

uninstall:
	target_dirs=(apngen git-xcp stpapp)
	$(foreach dir,$(target_dirs),rm -rf $(BIN_DIR)/$(dir);)

	target_files=(_gostp-build _gostp-define build.py gostp gostp-build gostp-update gostp-create)
	# @$(foreach file,$(target_files),rm -f $(BIN_DIR)/$(file);)
	$(foreach file, $(target_files), rm -f $(BIN_DIR)/$(file);)
	# unlink $(BIN_DIR)/$(LOADER)
