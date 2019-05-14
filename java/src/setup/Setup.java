package setup;

import os.OS;

import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.net.UnknownHostException;

public class Setup {
    public static OS OPERATING_SYSTEM;
    public static String CLIENT_ID;

    static {
        OPERATING_SYSTEM = determineOS();
        CLIENT_ID = determineClientID();
    }

    private static OS determineOS(){
        System.out.print("Determine OS: ");
        switch (System.getProperty("os.name")){
            case "Windows 10": return OS.WINDOWS_10;
            case "Linux": return OS.LINUX;
            default: throw new RuntimeException("Unsupported operating system!");
        }
    }

    private static String determineClientID(){
        try {
            InetAddress address = InetAddress.getLocalHost();
            NetworkInterface network = NetworkInterface.getByInetAddress(address);

            byte[] mac = network.getHardwareAddress();

            StringBuilder sb = new StringBuilder();
            for(int i=0; i < mac.length; i++){
                sb.append(String.format("%02X%s", mac[i], (i < mac.length - 1) ? "-" : ""));
            }

            return sb.toString();
        } catch (SocketException e) {
            e.printStackTrace();
        } catch (UnknownHostException e) {
            e.printStackTrace();
        }

        return null;
    }
}
