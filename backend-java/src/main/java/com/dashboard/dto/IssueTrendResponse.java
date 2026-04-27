package com.dashboard.dto;

import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class IssueTrendResponse {

    private List<SeriesData> series;

    @Data
    @Builder
    public static class SeriesData {
        private String name;
        private List<SeriesPoint> data;
    }

    @Data
    @Builder
    public static class SeriesPoint {
        private String x;
        private int y;
    }
}
