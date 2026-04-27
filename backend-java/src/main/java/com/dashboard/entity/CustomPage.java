package com.dashboard.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "custom_pages")
@Data
@NoArgsConstructor
public class CustomPage {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "project_id", nullable = false)
    private Project project;

    @Column(name = "page_key", nullable = false, length = 100)
    private String pageKey;

    @Column(name = "page_name", nullable = false)
    private String pageName;

    @Column(length = 50)
    private String icon;

    @Column(name = "sort_order")
    private int sortOrder = 0;

    @Column(name = "is_active")
    private boolean isActive = true;

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();
}
