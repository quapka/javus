TARGET = javacardversion
ANT = ant
GP = java -jar ${GO_PATH}

all: $(TARGET)

$(TARGET):
	-rm $(TARGET).cap
	$(ANT) $@

reinstall: $(TARGET) install

install:
	$(GP) --force --install $(TARGET).cap --verbose --debug

uninstall:
	$(GP) --uninstall $(TARGET).cap --verbose --debug

apdu:
	$(GP) --apdu 00a404000b0011223344AABB --verbose --debug

deploy: $(TARGET) install apdu
