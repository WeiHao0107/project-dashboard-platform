package com.dashboard.repository;

import com.dashboard.entity.Department;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface DepartmentRepository extends JpaRepository<Department, Long> {
    List<Department> findByProjectIdOrderByNameAsc(Long projectId);
}
