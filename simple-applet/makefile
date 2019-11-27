jcv = 222
TARGET = com.simple.jc$(jcv)
ANT = ant
GP = java -jar ${GO_PATH}
SELECT_CMD = 00a40400

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
	$(GP) --verbose --debug --apdu $(SELECT_CMD)080011223344AABBDD

deploy: $(TARGET) install apdu
