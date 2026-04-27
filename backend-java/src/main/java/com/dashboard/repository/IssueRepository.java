package com.dashboard.repository;

import com.dashboard.entity.Issue;
import org.springframework.data.jpa.repository.JpaRepository;

public interface IssueRepository extends JpaRepository<Issue, Long> {
    long countByProjectId(Long projectId);
}
