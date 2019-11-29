jcv = 212
PACKAGE = "com.metadatamanipulation"
TARGET = "$(PACKAGE).jc${jcv}"
ANT = ant
GP = java -jar "${GO_PATH}"
SELECT_CMD = "00a40400"
RID = "A0000000AA"
PIX = "5501"
AID = "A0000000AA5501"

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
	$(GP) --verbose --debug --apdu $(SELECT_CMD)07$(AID) $(emv)

deploy: $(TARGET) install apdu
