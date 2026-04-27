package com.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class ProjectDto {
    private Long id;
    private String key;
    private String name;
    private String description;
}
