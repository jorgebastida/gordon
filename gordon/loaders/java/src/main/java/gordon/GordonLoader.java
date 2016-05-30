package gordon;

import java.io.InputStreamReader;
import java.io.BufferedReader;
import java.io.IOException;
import java.lang.reflect.Method;
import java.lang.reflect.InvocationTargetException;
import com.amazonaws.services.lambda.runtime.LambdaLogger;
import com.amazonaws.services.lambda.runtime.ClientContext;
import com.amazonaws.services.lambda.runtime.CognitoIdentity;
import com.amazonaws.services.lambda.runtime.Context;

public class GordonLoader {


    public static class MockContext implements Context {

        public String getAwsRequestId(){
            return "AwsRequestId";
        }

        public String getLogGroupName(){
            return null;
        }

        public String getLogStreamName(){
            return null;
        }

        public String getFunctionName(){
            return "FunctionName";
        }

        public String getFunctionVersion(){
            return "current";
        }

        public String getInvokedFunctionArn(){
            return "";
        }

        public CognitoIdentity getIdentity(){
            return null;
        }

        public ClientContext getClientContext(){
            return null;
        }

        public int getRemainingTimeInMillis(){
            return 0;
        }

        public int getMemoryLimitInMB(){
            return 128;
        }

        public LambdaLogger getLogger(){
            return null;
        }

    }

    public static void main(String[] args) throws ClassNotFoundException, InstantiationException, IllegalAccessException, InvocationTargetException, NoSuchMethodException, IOException{
        // Split handler using AWS format module.class::handler
        String[] handler_elements = args[0].split("::");

        // Use reflectivity to get the class and method
        Class<?> clazz = Class.forName(handler_elements[0]);
        Object instance = clazz.newInstance();
        Class[] cArg = new Class[2];
        cArg[0] = String.class;
        cArg[1] = Context.class;
        Method m = clazz.getDeclaredMethod(handler_elements[1], cArg);
        Context context = new MockContext();

        // Read stdin
        BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
        String s;
        String input = "";
        while ((s = in.readLine()) != null && s.length() != 0){
            input += s;
        }
        // Call the user handler
        Object result = m.invoke(instance, input, context);
        System.out.println("output: " + result.toString());
    }

}
