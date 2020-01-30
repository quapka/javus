TARGET = "trans_bug"
ANT = ant
GP = java -jar "${GO_PATH}"
SELECT_CMD = "00a40400"
AID = "000000000102"

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
	$(GP) --verbose --debug --apdu $(SELECT_CMD)06$(AID) $(emv)

deploy: $(TARGET) install apdu
