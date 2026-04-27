package com.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class PageDto {
    private String pageId;
    private String title;
    private String icon;
    private int sortOrder;
}
