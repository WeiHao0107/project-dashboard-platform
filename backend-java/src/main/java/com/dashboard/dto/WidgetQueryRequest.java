package com.dashboard.dto;

import lombok.Data;

@Data
public class WidgetQueryRequest {
    private String projectKey;
    private String dataSource;
    private Filters filters;

    @Data
    public static class Filters {
        private Integer year;
        private Long departmentId;
    }
}
