import { Text } from "react-native";
import React, { ReactNode } from "react";

interface SubHeadingTextProps {
  children: ReactNode;
  style?: object;
  [key: string]: any;
}

const SubHeadingText: React.FC<SubHeadingTextProps> = ({
  children,
  style,
  ...props
}) => {
  return (
    <Text
      className={
        "text-slate-200 my-5 text-3xl font-bold tracking-wide mx-5 " +
        props.className
      }
      style={style}
      {...props}
    >
      {children}
    </Text>
  );
};

export default SubHeadingText;
