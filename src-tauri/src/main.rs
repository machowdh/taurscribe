// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::Command
use std::sync::mpsc::{sync_channel, Receiver};
use std::thread;
use command_group::CommandGroup
use tauri::api::process::Command as TCommand;
use tauri::WindowEvent

fn start_backend(receiver: Receiver<i32>){
  let t = TCommand::new_sidecar("main").expect("[Error] Failed to create 'main.exe' binary command"); 
  let mut group = Command::from(t).spawn().expect("[Error] spawning api server process.");

  thread::spawn(move || {
    loop{
      let s = receiver.recv();
      if s.unwrap() == -1{
        group.kill().expect("[Error] killing api server process.");
      }
    }
  });

  }

fn main() {

  let (tx, rx) = sync_channel(1);
  start_backend(rx);

  tauri::Builder::default()
    .on_window_event(|event| match event.event(){
      tauri::WindowEvent::Destroyed => {
        tx.send(-1).expect("[Error] sending messsage.");
        println!("[Event] App closed, shutting down API...");
      }
      _ => {}
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
