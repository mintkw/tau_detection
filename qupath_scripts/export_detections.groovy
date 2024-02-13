def server = getCurrentServer()

def imagename = server.getPath().split('/').last().replace('.svs', '').replace('[--series, 0]', '')
// def filedir = buildFilePath(/PATH_TO_OUTPUT_DIR/, String.format('%s_detections.txt', imagename))

File f = new File(filedir)

f.newWriter().withWriter {
    f << server.getWidth() + ' x ' + server.getHeight() << '\n'

    for (obj in getDetectionObjects()) {
        f << obj.getClassifications() << ' : ' << obj.getROI() << '\n'
    }
}