package helloworld;

import com.amazonaws.services.lambda.runtime.Context;

public class Hello {

    public static class EventClass {
        String key1;
        String key2;
        String key3;

        public String getKey1() {
            return key1;
        }

        public String getKey2() {
            return key2;
        }

        public String getKey3() {
            return key3;
        }

        public void setKey1(String key1) {
            this.key1 = key1;
        }

        public void setKey2(String key2) {
            this.key2 = key2;
        }

        public void setKey3(String key3) {
            this.key3 = key3;
        }

        public EventClass(String key1, String key2, String key3) {
            this.key1 = key1;
            this.key2 = key2;
            this.key3 = key3;
        }

        public EventClass() {}
    }

    public String handler(EventClass event, Context context) {
        System.out.println("value1 = " + event.key1);
        System.out.println("value2 = " + event.key2);
        System.out.println("value3 = " + event.key3);
        return String.format(event.key1);
    }

}
