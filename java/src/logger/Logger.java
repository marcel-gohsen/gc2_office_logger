package logger;


import java.io.File;
import java.io.IOException;

public abstract class Logger extends Thread{
    private boolean startLogging;

    public Logger(){
        File logDir = getLogDir();

        if(!logDir.exists()){
            boolean created = logDir.mkdirs();

            if(!created){
                throw new RuntimeException("Cannot create log directory");
            }
        }

        if(!logDir.isDirectory()){
            throw new RuntimeException("Log directory is not a directory");
        }

    }

    @Override
    public synchronized void start() {
        startLogging = true;
        super.start();
    }

    @Override
    public void run() {
        while (startLogging){
            try {
                log();
            } catch (IOException e) {
                e.printStackTrace();
            }

            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }

    }

    public void stopLogging() {
        startLogging = false;
    }

    protected abstract void log() throws IOException;

    protected abstract File getLogDir();
}
