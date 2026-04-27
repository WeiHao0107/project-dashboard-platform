package com.dashboard.repository;

import com.dashboard.entity.CustomPage;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface CustomPageRepository extends JpaRepository<CustomPage, Long> {
    List<CustomPage> findByProjectIdAndIsActiveTrueOrderBySortOrderAsc(Long projectId);
}
