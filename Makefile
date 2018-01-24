prefix 		= /usr/local
BIN_DIR   = $(prefix)/bin
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

	@echo "git-xcp*" > .madefiles

	rsync -avvi \
	--exclude-from=.makeignore \
	--delete \
	$(CURDIR)/* $(BIN_DIR) | grep ^\.[fd] | cut -c 11- >> .madefiles

uninstall:
	xargs -I{} sh -c 'rm -rf $(BIN_DIR)/{}' < .madefiles
	rm -rf .madefiles
