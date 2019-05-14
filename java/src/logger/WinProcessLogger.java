package logger;

import setup.Setup;

import java.io.*;
import java.nio.file.Paths;


public class WinProcessLogger extends Logger {
    private static final String SCRIPT = System.getenv("windir") + "\\system32\\tasklist.exe /FO CSV /V";
    private BufferedWriter outWriter;

    public WinProcessLogger() {
        super();
        try {
            outWriter = new BufferedWriter(
                    new FileWriter(Paths.get(getLogDir().toString(), "processlog.txt").toString()));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    @Override
    protected void log() throws IOException {
            Process process = Runtime.getRuntime().exec(SCRIPT);

            BufferedReader inReader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;

            while((line = inReader.readLine()) != null){
                outWriter.write(line + "\n");
            }

            outWriter.flush();
            inReader.close();
    }

    @Override
    protected File getLogDir() {
        return new File("logs/" + Setup.CLIENT_ID + "/");
    }

    public static void main(String[] args) {
        Logger logger = new WinProcessLogger();
//        logger.start();
//
//        try {
//            Thread.sleep(5000);
//        } catch (InterruptedException e) {
//            e.printStackTrace();
//        }
//
//        logger.stopLogging();
    }
}
