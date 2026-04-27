package com.dashboard.dto;

import lombok.Builder;
import lombok.Data;

import java.util.List;
import java.util.Map;

@Data
@Builder
public class WidgetDataResponse {

    private String dataSource;
    private String type;

    // chart fields
    private List<SeriesData> series;

    // table fields
    private List<ColumnDef> columns;
    private List<Map<String, Object>> rows;

    private ResultMeta meta;

    // ── nested types ──────────────────────────────────────

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

    @Data
    @Builder
    public static class ColumnDef {
        private String key;
        private String label;
        private String type;   // "string" | "number"
    }

    @Data
    @Builder
    public static class ResultMeta {
        private String computedAt;
        private boolean fromCache;
        private int totalRows;
    }
}
