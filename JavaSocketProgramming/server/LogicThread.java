package tcp;
import java.io.*;
import java.net.*;
import java.sql.*;
import net.sf.json.JSONObject;
import net.sf.json.JSONArray;



/**
 * 服务器端逻辑线程
 */
public class LogicThread extends Thread
{
    Socket socket;
    InputStream is;
    OutputStream os;

    public LogicThread(Socket socket) 
    {
        this.socket = socket;
        start(); //启动线程
    }

    // 线程处理逻辑
    public void run()
    {
        try
        {
            //初始化流
            os = socket.getOutputStream();
            is = socket.getInputStream();
            byte[] b = new byte[1024];
            int n = is.read(b);
            String recString=new String(b,0,n);
            System.out.println("客户端请求的影片："+recString);
            //调用子函数db_to_Json(),传进影片名，返回从数据库中取出信息组成的JsonArray对象
            JSONArray result= db_to_Json(recString);
                      
            //先将出现的次数传给客户端
            int num=result.size();
            System.out.println("出现广告的次数为:"+num);
            String nu = String.valueOf(num); 
            
            //string 转byte[]
            b=nu.getBytes("UTF-8");
            os.write(b);

            //JsonArray转为String类        
            String[] arr=new String[num];   
            for(int i=0;i<result.size();i++)
            {
                arr[i]=result.getString(i);
                byte [] midbytes=arr[i].getBytes("UTF-8");
                os.write(midbytes,0,midbytes.length);
                String Sign=null;

                //确认信息，告诉服务器已经处理完这一条，再传输下一条，OK是客户端发送的信息
                do
                {
                    byte[] c = new byte[1024];
                    n = is.read(c);
                    Sign=new String(c,0,n);
                    System.out.println(Sign);
                }while(!("OK".equals(Sign)));
                System.out.println(arr[i]);
            }
        }
        catch(Exception e)
        {
            e.printStackTrace();
        }
        finally
        {
            close();
        }
    }

    
    // 关闭流和连接
    private void close()
    {
        try
        {
            //关闭流和连接
            os.close();
            is.close();
            socket.close();
        }
        catch(Exception e) 
        {}
    }


    //访问数据库,将数据库返回数据转为JsonArray返回
    private JSONArray db_to_Json(String name)
    {
        // 驱动程序名
        String driver = "com.mysql.jdbc.Driver";
        // URL指向要访问的数据库名film
        String url = "jdbc:mysql://127.0.0.1:3306/film";
        // MySQL配置时的用户名
        String user = "root";
        // MySQL配置时的密码
        String password = "XXXX";

        // 创建一个json数组
        JSONArray array = new JSONArray();
        try
        {
            // 加载驱动程序
            Class.forName(driver);
            // 连接数据库
            Connection conn = DriverManager.getConnection(url, user, password);
            if(!conn.isClosed()) System.out.println("成功连接到数据库!");
            // statement用来执行SQL语句
            Statement statement = conn.createStatement();
            // 要执行的SQL语句,按时间查找广告出现的数据记录
            String sql = "select admoment,tv1,tv2,phone1,phone2 from captiontest where filmname='"+name+"' order by admoment";
            // 结果集
            ResultSet rs = statement.executeQuery(sql);

            //======将数据库返回对象转为JasonArray=====
            // 获取列数
            ResultSetMetaData metaData = rs.getMetaData();
            int columnCount = metaData.getColumnCount();

            // 遍历ResultSet中的每条数据
            while (rs.next())
            {
                JSONObject jsonObj = new JSONObject();
                // 遍历每一列
                for (int i = 1; i <= columnCount; i++) 
                {
                    String columnName = metaData.getColumnLabel(i);
                    String value = rs.getString(columnName);
                    jsonObj.put(columnName, value);
                }
                array.add(jsonObj);
            }
        }
        catch(ClassNotFoundException e)
        {
        System.out.println("Sorry,can`t find the Driver!");
        e.printStackTrace();
        }
        catch(SQLException e)
        {
        e.printStackTrace();
        }
        catch(Exception e)
        {
        e.printStackTrace();
        }
        return array;
    }
}
