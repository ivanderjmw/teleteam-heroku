import React from 'react';

import { Typography, Tag } from 'antd';
const { Title, Paragraph } = Typography;

const moment = require('moment');

const WelcomeMessage = (props) => {
    return (
        <Typography>
            <Title>Welcome back, {props.name}!</Title>
            {
                props.new ?
                <Paragraph>
                    You have no tasks created yet. Create a task from the telegram or from the group menu!
                </Paragraph>
                :
                <Paragraph>
                It's <b>{moment().format('LL')}</b>. Here are your upcoming tasks. You can click the <Tag color='blue'>group tag</Tag> to navigate to the group page, or click on one of your groups on the sidebar. The color represents how near the due date of a task is. <Tag color='#E05A3D'>Red</Tag>means in 3 days or below. <Tag color='#E0E32D'>Yellow</Tag>means in 3-5 days. <Tag color='#42DB3F'>Green</Tag>means in 5 or more days.
                </Paragraph>}
        </Typography>
    );
};

export default WelcomeMessage;