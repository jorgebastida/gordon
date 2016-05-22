package example;

import java.io.FileNotFoundException;
import java.util.Scanner;
import java.io.File;
import com.amazonaws.services.lambda.runtime.Context;
import org.json.JSONObject;


public class Hello {

    public static class EventClass {
        public EventClass() {}
    }

    public String handler(EventClass event, Context context) throws FileNotFoundException{
        JSONObject gordon_context = new JSONObject(
            new Scanner(new File(".context")).useDelimiter("\\A").next()
        );
        return gordon_context.getString("bucket");
    }

}
