# -*- coding: utf-8 -*-
"""
@file visualize.py
@brief Visualization module for rosbag data analysis.
This module provides functions to extract and visualize data from rosbag files,
including trajectory plots, sensor data time series, and statistical analysis.

@author Tomohiro MOTODA
@date 2025-01-20
@version 1.0
@note This script requires the following Python packages:
    - rosbag
    - matplotlib
    - numpy
    - pandas
    - geometry_msgs
    - sensor_msgs
    - tf2_msgs

***This script is written assisted by Copilot.***
"""

import rosbag
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os
from geometry_msgs.msg import PoseStamped, Twist
from sensor_msgs.msg import LaserScan, Image, CompressedImage
from tf2_msgs.msg import TFMessage
import argparse


def extract_pose_data(bag_path, pose_topic='/amcl_pose'):
    """
    Extract pose data from rosbag file.
    
    Args:
        bag_path (str): Path to the rosbag file
        pose_topic (str): ROS topic name for pose data
        
    Returns:
        pandas.DataFrame: DataFrame with timestamp, x, y, z, orientation data
    """
    pose_data = []
    
    try:
        with rosbag.Bag(bag_path, 'r') as bag:
            for topic, msg, t in bag.read_messages(topics=[pose_topic]):
                pose_data.append({
                    'timestamp': t.to_sec(),
                    'x': msg.pose.pose.position.x,
                    'y': msg.pose.pose.position.y,
                    'z': msg.pose.pose.position.z,
                    'qx': msg.pose.pose.orientation.x,
                    'qy': msg.pose.pose.orientation.y,
                    'qz': msg.pose.pose.orientation.z,
                    'qw': msg.pose.pose.orientation.w
                })
    except Exception as e:
        print(f"Error reading pose data from {bag_path}: {e}")
        return pd.DataFrame()
    
    df = pd.DataFrame(pose_data)
    if not df.empty:
        df['time'] = pd.to_datetime(df['timestamp'], unit='s')
    return df


def extract_velocity_data(bag_path, cmd_vel_topic='/cmd_vel'):
    """
    Extract velocity command data from rosbag file.
    
    Args:
        bag_path (str): Path to the rosbag file
        cmd_vel_topic (str): ROS topic name for velocity commands
        
    Returns:
        pandas.DataFrame: DataFrame with timestamp, linear and angular velocity data
    """
    vel_data = []
    
    try:
        with rosbag.Bag(bag_path, 'r') as bag:
            for topic, msg, t in bag.read_messages(topics=[cmd_vel_topic]):
                vel_data.append({
                    'timestamp': t.to_sec(),
                    'linear_x': msg.linear.x,
                    'linear_y': msg.linear.y,
                    'linear_z': msg.linear.z,
                    'angular_x': msg.angular.x,
                    'angular_y': msg.angular.y,
                    'angular_z': msg.angular.z
                })
    except Exception as e:
        print(f"Error reading velocity data from {bag_path}: {e}")
        return pd.DataFrame()
    
    df = pd.DataFrame(vel_data)
    if not df.empty:
        df['time'] = pd.to_datetime(df['timestamp'], unit='s')
    return df


def extract_laser_data(bag_path, laser_topic='/scan'):
    """
    Extract laser scan data statistics from rosbag file.
    
    Args:
        bag_path (str): Path to the rosbag file
        laser_topic (str): ROS topic name for laser scan data
        
    Returns:
        pandas.DataFrame: DataFrame with timestamp and laser statistics
    """
    laser_data = []
    
    try:
        with rosbag.Bag(bag_path, 'r') as bag:
            for topic, msg, t in bag.read_messages(topics=[laser_topic]):
                ranges = np.array(msg.ranges)
                # Filter out inf and nan values
                valid_ranges = ranges[(ranges != float('inf')) & (~np.isnan(ranges))]
                
                if len(valid_ranges) > 0:
                    laser_data.append({
                        'timestamp': t.to_sec(),
                        'min_range': np.min(valid_ranges),
                        'max_range': np.max(valid_ranges),
                        'mean_range': np.mean(valid_ranges),
                        'std_range': np.std(valid_ranges),
                        'valid_points': len(valid_ranges),
                        'total_points': len(ranges)
                    })
    except Exception as e:
        print(f"Error reading laser data from {bag_path}: {e}")
        return pd.DataFrame()
    
    df = pd.DataFrame(laser_data)
    if not df.empty:
        df['time'] = pd.to_datetime(df['timestamp'], unit='s')
    return df


def plot_trajectory(pose_df, title="Robot Trajectory", save_path=None):
    """
    Plot 2D trajectory from pose data.
    
    Args:
        pose_df (pandas.DataFrame): DataFrame with pose data
        title (str): Plot title
        save_path (str): Path to save the plot (optional)
    """
    if pose_df.empty:
        print("No pose data to plot")
        return
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Plot trajectory
    ax.plot(pose_df['x'], pose_df['y'], 'b-', alpha=0.7, linewidth=1.5)
    ax.scatter(pose_df['x'].iloc[0], pose_df['y'].iloc[0], 
               color='green', s=100, marker='o', label='Start', zorder=5)
    ax.scatter(pose_df['x'].iloc[-1], pose_df['y'].iloc[-1], 
               color='red', s=100, marker='s', label='End', zorder=5)
    
    # Add annotations
    ax.text(pose_df['x'].iloc[0], pose_df['y'].iloc[0], 'START', 
            fontsize=8, ha='center', va='bottom')
    ax.text(pose_df['x'].iloc[-1], pose_df['y'].iloc[-1], 'END', 
            fontsize=8, ha='center', va='bottom')
    
    ax.set_xlabel('X [m]')
    ax.set_ylabel('Y [m]')
    ax.set_title(f'{title} - Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.axis('equal')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def plot_velocity_time_series(vel_df, title="Velocity Commands", save_path=None):
    """
    Plot velocity commands over time.
    
    Args:
        vel_df (pandas.DataFrame): DataFrame with velocity data
        title (str): Plot title
        save_path (str): Path to save the plot (optional)
    """
    if vel_df.empty:
        print("No velocity data to plot")
        return
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Linear velocity
    ax1.plot(vel_df['time'], vel_df['linear_x'], 'b-', label='Linear X', alpha=0.8)
    ax1.plot(vel_df['time'], vel_df['linear_y'], 'g-', label='Linear Y', alpha=0.8)
    ax1.set_ylabel('Linear Velocity [m/s]')
    ax1.set_title(f'{title} - Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Angular velocity
    ax2.plot(vel_df['time'], vel_df['angular_z'], 'r-', label='Angular Z', alpha=0.8)
    ax2.set_ylabel('Angular Velocity [rad/s]')
    ax2.set_xlabel('Time')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def plot_laser_statistics(laser_df, title="Laser Scan Statistics", save_path=None):
    """
    Plot laser scan statistics over time.
    
    Args:
        laser_df (pandas.DataFrame): DataFrame with laser statistics
        title (str): Plot title
        save_path (str): Path to save the plot (optional)
    """
    if laser_df.empty:
        print("No laser data to plot")
        return
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10), sharex=True)
    
    # Min/Max ranges
    ax1.plot(laser_df['time'], laser_df['min_range'], 'r-', label='Min Range', alpha=0.8)
    ax1.plot(laser_df['time'], laser_df['max_range'], 'b-', label='Max Range', alpha=0.8)
    ax1.set_ylabel('Range [m]')
    ax1.set_title('Min/Max Laser Ranges')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Mean range
    ax2.plot(laser_df['time'], laser_df['mean_range'], 'g-', alpha=0.8)
    ax2.set_ylabel('Mean Range [m]')
    ax2.set_title('Mean Laser Range')
    ax2.grid(True, alpha=0.3)
    
    # Standard deviation
    ax3.plot(laser_df['time'], laser_df['std_range'], 'm-', alpha=0.8)
    ax3.set_ylabel('Std Range [m]')
    ax3.set_title('Laser Range Standard Deviation')
    ax3.set_xlabel('Time')
    ax3.grid(True, alpha=0.3)
    
    # Valid points ratio
    valid_ratio = laser_df['valid_points'] / laser_df['total_points']
    ax4.plot(laser_df['time'], valid_ratio, 'c-', alpha=0.8)
    ax4.set_ylabel('Valid Points Ratio')
    ax4.set_title('Valid Laser Points Ratio')
    ax4.set_xlabel('Time')
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(0, 1)
    
    fig.suptitle(f'{title} - Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def analyze_rosbag(bag_path, output_dir='./visualization_output'):
    """
    Comprehensive analysis and visualization of rosbag data.
    
    Args:
        bag_path (str): Path to the rosbag file
        output_dir (str): Directory to save output files
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    bag_name = os.path.splitext(os.path.basename(bag_path))[0]
    
    print(f"Analyzing rosbag: {bag_path}")
    
    # Extract data from different topics
    print("Extracting pose data...")
    pose_df = extract_pose_data(bag_path)
    
    print("Extracting velocity data...")
    vel_df = extract_velocity_data(bag_path)
    
    print("Extracting laser data...")
    laser_df = extract_laser_data(bag_path)
    
    # Generate plots
    if not pose_df.empty:
        print("Generating trajectory plot...")
        trajectory_path = os.path.join(output_dir, f'{bag_name}_trajectory.png')
        plot_trajectory(pose_df, f"Trajectory - {bag_name}", trajectory_path)
        
        # Save pose data to CSV
        pose_csv_path = os.path.join(output_dir, f'{bag_name}_pose_data.csv')
        pose_df.to_csv(pose_csv_path, index=False)
        print(f"Pose data saved to: {pose_csv_path}")
    
    if not vel_df.empty:
        print("Generating velocity plot...")
        velocity_path = os.path.join(output_dir, f'{bag_name}_velocity.png')
        plot_velocity_time_series(vel_df, f"Velocity - {bag_name}", velocity_path)
        
        # Save velocity data to CSV
        vel_csv_path = os.path.join(output_dir, f'{bag_name}_velocity_data.csv')
        vel_df.to_csv(vel_csv_path, index=False)
        print(f"Velocity data saved to: {vel_csv_path}")
    
    if not laser_df.empty:
        print("Generating laser statistics plot...")
        laser_path = os.path.join(output_dir, f'{bag_name}_laser_stats.png')
        plot_laser_statistics(laser_df, f"Laser Stats - {bag_name}", laser_path)
        
        # Save laser data to CSV
        laser_csv_path = os.path.join(output_dir, f'{bag_name}_laser_data.csv')
        laser_df.to_csv(laser_csv_path, index=False)
        print(f"Laser data saved to: {laser_csv_path}")
    
    # Generate summary report
    summary_path = os.path.join(output_dir, f'{bag_name}_summary.txt')
    with open(summary_path, 'w') as f:
        f.write(f"Rosbag Analysis Summary\n")
        f.write(f"=======================\n")
        f.write(f"Bag file: {bag_path}\n")
        f.write(f"Analysis date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if not pose_df.empty:
            duration = (pose_df['timestamp'].max() - pose_df['timestamp'].min())
            distance = np.sqrt(np.diff(pose_df['x'])**2 + np.diff(pose_df['y'])**2).sum()
            f.write(f"Pose Data:\n")
            f.write(f"  - Duration: {duration:.2f} seconds\n")
            f.write(f"  - Total distance: {distance:.2f} meters\n")
            f.write(f"  - Start position: ({pose_df['x'].iloc[0]:.2f}, {pose_df['y'].iloc[0]:.2f})\n")
            f.write(f"  - End position: ({pose_df['x'].iloc[-1]:.2f}, {pose_df['y'].iloc[-1]:.2f})\n\n")
        
        if not vel_df.empty:
            f.write(f"Velocity Data:\n")
            f.write(f"  - Max linear velocity: {vel_df['linear_x'].max():.2f} m/s\n")
            f.write(f"  - Max angular velocity: {vel_df['angular_z'].abs().max():.2f} rad/s\n")
            f.write(f"  - Mean linear velocity: {vel_df['linear_x'].mean():.2f} m/s\n\n")
        
        if not laser_df.empty:
            f.write(f"Laser Data:\n")
            f.write(f"  - Mean range: {laser_df['mean_range'].mean():.2f} m\n")
            f.write(f"  - Min range encountered: {laser_df['min_range'].min():.2f} m\n")
            f.write(f"  - Max range encountered: {laser_df['max_range'].max():.2f} m\n")
    
    print(f"Analysis complete! Results saved to: {output_dir}")
    print(f"Summary report: {summary_path}")


def main():
    parser = argparse.ArgumentParser(description="Visualize rosbag data")
    parser.add_argument('bag_path', help='Path to the rosbag file')
    parser.add_argument('--output_dir', default='./visualization_output', 
                       help='Directory to save visualization outputs')
    parser.add_argument('--pose_topic', default='/amcl_pose', 
                       help='ROS topic for pose data')
    parser.add_argument('--cmd_vel_topic', default='/cmd_vel', 
                       help='ROS topic for velocity commands')
    parser.add_argument('--laser_topic', default='/scan', 
                       help='ROS topic for laser scan data')
    parser.add_argument('--show', action='store_true', 
                       help='Show plots instead of just saving them')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.bag_path):
        print(f"Error: Bag file not found: {args.bag_path}")
        return
    
    # Run comprehensive analysis
    analyze_rosbag(args.bag_path, args.output_dir)
    
    if args.show:
        plt.show()


if __name__ == "__main__":
    main()