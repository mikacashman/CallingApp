
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
 * <p>Original spec-file type: CallingParams</p>
 * <pre>
 * Insert your typespec information here.
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "workspace",
    "fbamodel_id",
    "media",
    "fbaOutput_id"
})
public class CallingParams {

    @JsonProperty("workspace")
    private String workspace;
    @JsonProperty("fbamodel_id")
    private String fbamodelId;
    @JsonProperty("media")
    private String media;
    @JsonProperty("fbaOutput_id")
    private String fbaOutputId;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("workspace")
    public String getWorkspace() {
        return workspace;
    }

    @JsonProperty("workspace")
    public void setWorkspace(String workspace) {
        this.workspace = workspace;
    }

    public CallingParams withWorkspace(String workspace) {
        this.workspace = workspace;
        return this;
    }

    @JsonProperty("fbamodel_id")
    public String getFbamodelId() {
        return fbamodelId;
    }

    @JsonProperty("fbamodel_id")
    public void setFbamodelId(String fbamodelId) {
        this.fbamodelId = fbamodelId;
    }

    public CallingParams withFbamodelId(String fbamodelId) {
        this.fbamodelId = fbamodelId;
        return this;
    }

    @JsonProperty("media")
    public String getMedia() {
        return media;
    }

    @JsonProperty("media")
    public void setMedia(String media) {
        this.media = media;
    }

    public CallingParams withMedia(String media) {
        this.media = media;
        return this;
    }

    @JsonProperty("fbaOutput_id")
    public String getFbaOutputId() {
        return fbaOutputId;
    }

    @JsonProperty("fbaOutput_id")
    public void setFbaOutputId(String fbaOutputId) {
        this.fbaOutputId = fbaOutputId;
    }

    public CallingParams withFbaOutputId(String fbaOutputId) {
        this.fbaOutputId = fbaOutputId;
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
        return ((((((((((("CallingParams"+" [workspace=")+ workspace)+", fbamodelId=")+ fbamodelId)+", media=")+ media)+", fbaOutputId=")+ fbaOutputId)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
