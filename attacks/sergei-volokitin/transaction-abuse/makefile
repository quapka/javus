TARGET = "com.transaction_ref"
ANT = ant
GP = java -jar "${GO_PATH}"
SELECT_CMD = 00a40400
AID = "A0000000333301"

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
	$(GP) --verbose --debug --apdu $(SELECT_CMD)07$(AID)

deploy: $(TARGET) install apdu
