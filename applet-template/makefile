TARGET = "<PackageName>"
ANT = ant
GP = java -jar "${GO_PATH}"
SELECT_CMD = 00a40400
AID = "<RID><PIX>"

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
	$(GP) --verbose --debug --apdu $(SELECT_CMD)<DATA_LEN>$(AID)

deploy: $(TARGET) install apdu
