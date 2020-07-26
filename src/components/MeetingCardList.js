import React, { Component } from 'react';
import { Empty } from 'antd';
import MeetingCard from "./MeetingCard";

const MeetingCardList = (props) =>{
    const meetings = props.meetings;
    const meetingCards = meetings.sort(function(a, b) {
        var keyA = new Date(a.deadline),
          keyB = new Date(b.deadline);
        // Compare the 2 dates
        if (keyA < keyB) return -1;
        if (keyA > keyB) return 1;
        return 0;
      })
    .map((meeting) =>
        <MeetingCard meeting={meeting} onChange={props.onChange} colorCodeTags={props.colorCodeTags}/>
    );
    return (
        <div>{ !(meetings.length == 0) ?
          meetingCards :
          <Empty/>
        }</div>
    );
}

export default MeetingCardList;