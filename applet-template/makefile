jcv = 212
PACKAGE = com.<PackageName>
TARGET = "$(PACKAGE).jc${jcv}"
ANT = ant
GP = java -jar "${GO_PATH}"
SELECT_CMD = "00a40400"
RID = "<RID>"
PIX = "<PIX>"
AID = "<RID><PIX>"

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
	$(GP) --verbose --debug --apdu $(SELECT_CMD)<DATA_LEN>$(AID) $(emv)

deploy: $(TARGET) install apdu
