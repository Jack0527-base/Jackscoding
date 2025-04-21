package me.jack;
//public class Main {
//    public static void main(String[] args) {
//        int[] arr1 = {1, -2, 3, 5, -1};
//        int[] arr2 = {1, -2, 3, -8, 5, 1};
//        int[] arr3 = {1, -2, 3, -2, 5, 1};
//
//        System.out.println("Maxsum=" + maxSum(arr1));
//        System.out.println("Maxsum=" + maxSum(arr2));
//        System.out.println("Maxsum=" + maxSum(arr3));
//    }
//
//    public static int maxSum(int[] arr) {
//        int max = arr[0];
//        int currentMax = arr[0];
//
//        for (int i = 1; i < arr.length; i++) {
//            currentMax = Math.max(arr[i], currentMax + arr[i]);
//            max = Math.max(max, currentMax);
//        }
//
//        return max;
//    }
//}

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

public class Main {
    // 主方法，程序入口
    public static void main(String[] args) {
        // 定义日期的年、月、日
        int year = 2023;
        int month = 10;
        int day = 5;

        // 调用 nextDate 方法获取明天的日期
        String nextDate = getNextDate(year, month, day);
        // 输出明天的日期
        System.out.println("明天的日期是: " + nextDate);
    }

    /**
     * 计算给定日期的下一天日期
     * @param year 年份
     * @param month 月份
     * @param day 日期
     * @return 下一天日期的字符串，格式为 "yyyy-MM-dd"
     */
    public static String getNextDate(int year, int month, int day) {
        // 创建 LocalDate 对象表示给定日期
        LocalDate date = LocalDate.of(year, month, day);
        // 计算下一天的日期
        LocalDate nextDay = date.plusDays(1);
        // 定义日期格式化器
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");
        // 格式化下一天的日期并返回
        return nextDay.format(formatter);
    }
}