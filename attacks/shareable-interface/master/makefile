jcv = 212
PACKAGE = "com.shareableinterfacemaster"
TARGET = "$(PACKAGE).jc${jcv}"
ANT = ant
GP = java -jar "${GO_PATH}"
SELECT_CMD = "00a40400"
RID = "0000000001"
PIX = "04"
AID = "000000000104"

all: $(TARGET)

$(TARGET):
	-rm $(TARGET).cap
	$(ANT) $@

versions:
	-rm $(PACKAGE).jc212.cap
	$(ANT) $(PACKAGE).jc212

	-rm $(PACKAGE).jc221.cap
	$(ANT) $(PACKAGE).jc221

	-rm $(PACKAGE).jc222.cap
	$(ANT) $(PACKAGE).jc222

	-rm $(PACKAGE).jc305u3.cap
	$(ANT) $(PACKAGE).jc305u3

reinstall: $(TARGET) install

install:
	$(GP) --force --install $(TARGET).cap --verbose --debug $(emv)

uninstall:
	$(GP) --uninstall $(TARGET).cap --verbose --debug $(emv)

apdu:
	$(GP) --verbose --debug --apdu $(SELECT_CMD)06$(AID) $(emv)

deploy: $(TARGET) install apdu
