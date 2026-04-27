package com.dashboard.repository;

import com.dashboard.entity.Member;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface MemberRepository extends JpaRepository<Member, Long> {

    @Query("SELECT m FROM Member m JOIN m.department d WHERE d.project.id = :projectId ORDER BY m.name")
    List<Member> findByProjectId(@Param("projectId") Long projectId);

    @Query("SELECT m FROM Member m WHERE m.department.id = :deptId ORDER BY m.name")
    List<Member> findByDepartmentId(@Param("deptId") Long deptId);
}
