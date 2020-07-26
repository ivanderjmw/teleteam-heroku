import React, { Component } from 'react';
import { Empty } from 'antd';
import TaskCard from "./TaskCard";

const TaskCardList = (props) =>{
    const members = props.members
    const tasks = props.tasks;
    const taskCards = props.tasks.sort(function(a, b) {
        var keyA = new Date(a.deadline),
          keyB = new Date(b.deadline);
        // Compare the 2 dates
        if (keyA < keyB) return -1;
        if (keyA > keyB) return 1;
        return 0;
      })
    .map((task) =>
        <TaskCard 
          task={task} 
          members={members} 
          colorCodeTag={props.colorCodeTags} 
          onChange={props.onChange}
          viewGroup={props.viewGroup ? true : false}/>
    );
    return (
        <div>{ !(tasks.length == 0) ? 
          taskCards :
          <Empty />}</div>
    );
}

export default TaskCardList;