package example;

import com.amazonaws.services.lambda.runtime.Context;
import org.json.JSONObject;

public class Hello {

    public static class EventClass {
        String key1;

        public String getKey1() {
            return key1;
        }

        public void setKey1(String key1) {
            this.key1 = key1;
        }

        public EventClass(String key1) {
            this.key1 = key1;
        }

        public EventClass() {}
    }

    public String handler(EventClass event, Context context) {
        System.out.println("Loading function");
        System.out.println("value1 = " + event.key1);
        return String.format(event.key1);
    }

    public String handler(String json_event, Context context) {
        JSONObject event_data = new JSONObject(json_event);
        EventClass event = new EventClass(
            event_data.getString("key1")
        );
        return this.handler(event, context);
    }

}
