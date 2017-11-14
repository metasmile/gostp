prefix = /usr/local
BIN_DIR   = $(prefix)/bin
LOADER    = gostp
COMMANDS  = gostp-build gostp-update gostp-create

all:
	@echo "usage: make [install|uninstall]"

install:
	#apng2gif
	#brew link --overwrite apng2gif
	#ffmpeg
	install -d -m 0755 $(BIN_DIR)
	install -m 0755 $(LOADER) $(BIN_DIR)
	install -m 0644 $(COMMANDS) $(BIN_DIR)

uninstall:
	test -d $(BIN_DIR) && \
	cd $(BIN_DIR) && \
	rm -f $(LOADER) $(COMMANDS)
