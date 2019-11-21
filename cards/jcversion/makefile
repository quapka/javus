TARGET = javacardversion
ANT = ant
GP = java -jar ${GO_PATH}

all: $(TARGET)

$(TARGET):
	-rm $(TARGET).cap
	$(ANT) $@

reinstall: $(TARGET) install

install:
	$(GP) --force --install $(TARGET).cap --verbose --debug $(emv)

uninstall:
	$(GP) --uninstall $(TARGET).cap --verbose --debug $(emv)

apdu:
	$(GP) --apdu 00a40400060011223344AABB --verbose --debug $(emv)

deploy: $(TARGET) install apdu
