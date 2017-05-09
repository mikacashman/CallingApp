
package us.kbase.callingapp;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: CallingResults</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "temp"
})
public class CallingResults {

    @JsonProperty("temp")
    private String temp;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("temp")
    public String getTemp() {
        return temp;
    }

    @JsonProperty("temp")
    public void setTemp(String temp) {
        this.temp = temp;
    }

    public CallingResults withTemp(String temp) {
        this.temp = temp;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((("CallingResults"+" [temp=")+ temp)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
