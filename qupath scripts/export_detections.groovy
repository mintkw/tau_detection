def server = getCurrentServer()

def imagename = server.getPath().split('/').last().replace('.svs', '').replace('[--series, 0]', '')
def filedir = "/Users/kwanwynn.tan.21/Desktop/qupath/annotations" + '/' + String.format('%s_detections.txt', imagename)

File ann = new File(filedir)

ann.newWriter().withWriter {
    ann << server.getWidth() + ' x ' + server.getHeight() << '\n'

    for (annotation in getDetectionObjects()) {
        ann << annotation.getClassifications() << ' : ' << annotation.getROI() << '\n'
    }
}