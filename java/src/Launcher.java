import logger.Logger;
import logger.WinProcessLogger;
import os.OS;
import setup.Setup;

import java.util.ArrayList;
import java.util.List;

public class Launcher {
    private List<Logger> logger;

    public Launcher(){
        System.out.println("Initialize...");
        logger = new ArrayList<>();

        if(Setup.OPERATING_SYSTEM == OS.LINUX){
            System.out.println("LINUX");
        }

        if(Setup.OPERATING_SYSTEM == OS.WINDOWS_10){
            System.out.println("WINDOWS 10");

            logger.add(new WinProcessLogger());
        }

        Runtime.getRuntime().addShutdownHook(new Thread(){
            @Override
            public void run() {
                System.out.println("Shutdown logger...");
                for(Logger logger: logger){
                    logger.stopLogging();
                }
            }
        });
    }

    public void run(){
        for(Logger logger: logger){
            logger.start();
        }

        try {
            Thread.sleep(5000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        for(Logger logger: logger){
            logger.stopLogging();
        }
    }

    public static void main(String[] args) {
        Launcher launcher = new Launcher();
        launcher.run();
    }
}


