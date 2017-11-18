prefix = /usr/local
BIN_DIR   = $(prefix)/bin
LOADER    = gostp
COMMANDS  = gostp-build gostp-update gostp-create

all:
	@echo "usage: make [install|uninstall]"

install:
	brew list apng2gif &>/dev/null || brew install apng2gif
	brew list ffmpeg &>/dev/null || brew install ffmpeg
	git clone https://github.com/metasmile/git-xcp.git && cd git-xcp && make install && cd - && rm -rf ./git-xcp
	install -d -m 0755 $(BIN_DIR)
	install -m 0755 $(LOADER) $(BIN_DIR)
	install -m 0644 $(COMMANDS) $(BIN_DIR)

uninstall:
	test -d $(BIN_DIR) && \
	cd $(BIN_DIR) && \
	rm -f $(LOADER) $(COMMANDS)
