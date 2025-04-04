import { Text } from "react-native";
import React, { ReactNode } from "react";

interface HeadingTextProps {
  children: ReactNode;
  style?: object;
  [key: string]: any;
}

const HeadingText: React.FC<HeadingTextProps> = ({
  children,
  style,
  ...props
}) => {
  return (
    <Text
      className="text-5xl font-semibold text-slate-100 px-3"
      style={style}
      {...props}
    >
      {children}
    </Text>
  );
};

export default HeadingText;
