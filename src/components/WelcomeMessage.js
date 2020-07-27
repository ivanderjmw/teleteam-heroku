import React from 'react';

import { Typography, Tag } from 'antd';
const { Title, Paragraph } = Typography;

const moment = require('moment');

const WelcomeMessage = (props) => {
    return (
        <Typography>
            <Title>Hello, {props.name}!</Title>
            {
                props.new ?
                <Paragraph>
                    <b>Welcome to Teleteam!</b> 🎉🎉<br /><br />

                    Your Telegram account is already on our records.<br /><br />

                    To start using Teleteam in your groups, please<br />

                    1. Add our bot <Tag color='blue'>@teleteam_bot</Tag> to your group.<br />
                    2. <Tag color='blue'>/start</Tag> in the group to initialise the group.<br />
                    3. Ask each member to <Tag color='blue'>/join</Tag> so that we know who's inside the group!
                    <br /><br />
                    <b>Creating tasks and meetings</b><br />
                    On this web app, you can select a group and click on the "New Task" or "New Meeting" button 
                    to create a new task or meeting. Alternatively, you can use the <Tag color='blue'>/createtask</Tag> or <Tag color='blue'>/createmeeting</Tag>
                    bot command inside one of the groups.<br /><br />

                    We will notify and set a reminder for everyone when a new task or meeting is created.<br /><br />

                    If you prefer to not receive any notifications or reminders, please go to the Settings Page
                    on the menu on the left.<br /><br />

                    You have no tasks created yet. Create a task from the group menu or using our bot!
                </Paragraph>
                :
                <Paragraph>
                It's <b>{moment().format('LL')}</b>. Here are your upcoming tasks. 
                <br />
                You can click the <Tag color='blue'>group tag</Tag> to navigate to the group page, or click on one of your groups on the sidebar. 
                <br />The color represents how near the due date of a task is. 
                <Tag color='#E05A3D'>Red</Tag>means in 3 days or earlier. 
                <Tag color='#E0E32D'>Yellow</Tag>means in 3-5 days. 
                <Tag color='#42DB3F'>Green</Tag>means in 5 or more days.
                </Paragraph>}
        </Typography>
    );
};

export default WelcomeMessage;