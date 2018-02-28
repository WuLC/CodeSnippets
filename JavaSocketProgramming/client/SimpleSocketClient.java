import java.io.*;
import java.net.*;
import net.sf.json.JSONObject;
import net.sf.json.JSONArray;

/*
 * Socket 客户端
 */
public class SimpleSocketClient 
{
    public static void main(String[] args) 
    {
        Socket socket = null;
        InputStream is = null;
        OutputStream os = null;
        String serverIP = "202.38.206.116";
        int port = 10000;
        String data = "变形金刚";
        try 
        {
            socket = new Socket(serverIP,port);
            os = socket.getOutputStream();
            byte[] a=data.getBytes("UTF-8");
            os.write(a);
            is = socket.getInputStream();
            byte[] b = new byte[1024];
            int n = is.read(b);
            String recString=new String(b,0,n);
                       
            int num=Integer.valueOf(recString).intValue();
            String[] arr=new String[num];
            
            JSONArray array = new JSONArray();
            String sign="OK"; 

            for (int i=0;i<num ;i++)
            {
                int m = is.read(b);
                arr[i]=new String(b, 0, m, "UTF-8");
                JSONObject jsonObj=JSONObject.fromObject(arr[i]);
                array.add(jsonObj);
                os.write(sign.getBytes("UTF-8"));
                System.out.println(arr[i]+"\n");
            }

            for (int i = 0; i < array.size(); i++) 
            {
                JSONObject jo = (JSONObject)array.get(i);
                System.out.println(jo.get("admoment"));
            }
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }
        finally
        {
            try
            {
                is.close();
                os.close();
                socket.close();
            }
            catch(Exception e2)
            {}
        }
    }
}