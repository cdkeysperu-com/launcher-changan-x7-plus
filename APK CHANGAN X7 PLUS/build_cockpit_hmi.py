# -*- coding: utf-8 -*-
"""
Generador Maestro del Cockpit HMI Changan X7 Plus Custom Launcher (1920x720)
Versión Refinada: Réplica 1:1 exacta de la referencia sin recuadros anidados,
con etiquetas tipográficas limpias en las tarjetas y barra de favoritos original.
"""
import os
import shutil

html_content = r'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Changan X7 Plus — Custom HMI Cockpit Launcher</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary-cyan: #38bdf8;
      --primary-blue: #2563eb;
      --dock-width: 104px;
      --bg-dark: #030712;
      --font-main: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
      -webkit-user-select: none;
      -webkit-tap-highlight-color: transparent;
    }

    html, body {
      width: 100vw;
      height: 100vh;
      max-width: 1920px;
      max-height: 720px;
      overflow: hidden;
      background-color: var(--bg-dark);
      color: #f8fafc;
      font-family: var(--font-main);
    }

    /* FULL SCREEN COCKPIT CONTAINER (1920x720) */
    .cockpit-container {
      position: relative;
      width: 100%;
      height: 100%;
      display: flex;
      background-color: #030712;
      background-image: 
        linear-gradient(90deg, rgba(3, 7, 18, 0.88) 0%, rgba(3, 7, 18, 0.65) 32%, rgba(3, 7, 18, 0.25) 60%, rgba(3, 7, 18, 0.05) 85%),
        url('assets/bg_cockpit.png');
      background-position: right center;
      background-repeat: no-repeat;
      background-size: cover;
      animation: cockpitFadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
    }

    @keyframes cockpitFadeIn {
      from { opacity: 0; transform: scale(0.99); }
      to { opacity: 1; transform: scale(1); }
    }

    /* LEFT VERTICAL DOCK (Changan Tweaker Pro Style) */
    .cockpit-dock {
      width: var(--dock-width);
      height: 100%;
      background: rgba(6, 10, 18, 0.86);
      backdrop-filter: blur(28px);
      -webkit-backdrop-filter: blur(28px);
      border-right: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 14px 0 12px 0;
      z-index: 100;
      flex-shrink: 0;
    }

    .dock-items-wrapper {
      display: flex;
      flex-direction: column;
      gap: 8px;
      width: 100%;
      height: 100%;
      align-items: center;
      justify-content: space-evenly;
    }

    .dock-btn {
      width: 86px;
      height: 72px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 4px;
      border-radius: 16px;
      color: #94a3b8;
      background: transparent;
      border: 1px solid transparent;
      cursor: pointer;
      position: relative;
      transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
      text-decoration: none;
    }

    .dock-btn svg {
      width: 25px;
      height: 25px;
      stroke-width: 2;
      transition: transform 0.22s, color 0.22s;
    }

    .dock-btn span {
      font-size: 11.5px;
      font-weight: 500;
      letter-spacing: 0.2px;
      transition: color 0.22s;
    }

    .dock-btn:hover {
      color: #f1f5f9;
      background: rgba(255, 255, 255, 0.06);
      border-color: rgba(255, 255, 255, 0.1);
    }

    .dock-btn:active {
      transform: scale(0.94);
    }

    /* ACTIVE DOCK BUTTON */
    .dock-btn.active {
      color: #ffffff;
      background: linear-gradient(135deg, rgba(29, 78, 216, 0.5) 0%, rgba(15, 23, 42, 0.75) 100%);
      border: 1.5px solid rgba(56, 189, 248, 0.5);
      box-shadow: 0 0 25px rgba(37, 99, 235, 0.4), inset 0 0 14px rgba(56, 189, 248, 0.2);
    }

    .dock-btn.active::before {
      content: '';
      position: absolute;
      left: -9px;
      top: 14px;
      bottom: 14px;
      width: 4px;
      background: #38bdf8;
      border-radius: 0 4px 4px 0;
      box-shadow: 0 0 14px #38bdf8, 0 0 22px #0284c7;
    }

    .dock-btn.active svg {
      color: #ffffff;
      filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.7));
    }

    /* RIGHT MAIN CONTENT AREA */
    .cockpit-main {
      flex: 1;
      height: 100%;
      position: relative;
      display: flex;
      flex-direction: column;
      padding: 10px 18px 8px 20px;
      overflow: hidden;
      min-width: 0;
    }

    /* STATUS BAR (Top Right) */
    .cockpit-statusbar {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 18px;
      z-index: 50;
      height: 32px;
      margin-bottom: 2px;
    }

    .status-icons {
      display: flex;
      align-items: center;
      gap: 16px;
      color: #e2e8f0;
    }

    .status-icon-btn {
      background: transparent;
      border: none;
      color: #e2e8f0;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: color 0.2s, transform 0.2s;
    }

    .status-icon-btn:hover {
      color: #38bdf8;
      transform: scale(1.1);
    }

    .status-icon-btn svg {
      width: 18px;
      height: 18px;
    }

    .status-clock {
      font-family: var(--font-main);
      font-size: 16px;
      font-weight: 600;
      color: #f1f5f9;
      letter-spacing: 0.5px;
      margin-left: 2px;
    }

    /* SLIDER CONTAINER WITH ISOLATED VIEWPORT */
    .slider-viewport {
      flex: 1;
      width: 100%;
      height: calc(100% - 34px);
      overflow: hidden;
      position: relative;
      min-height: 0;
    }

    .pages-slider {
      display: flex;
      width: 200%;
      height: 100%;
      transition: transform 0.45s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .page {
      width: 50%;
      max-width: 50%;
      height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      min-height: 0;
      padding-top: 2px;
      flex-shrink: 0;
    }

    /* HERO SECTION (Clock + Music Widget) */
    .hero-section {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
      margin-top: 0;
      margin-bottom: 8px;
    }

    .hero-clock-block {
      display: flex;
      flex-direction: column;
    }

    .hero-clock {
      font-size: 78px;
      font-weight: 700;
      line-height: 0.88;
      letter-spacing: -2px;
      color: #ffffff;
      text-shadow: 0 4px 28px rgba(0, 0, 0, 0.95);
    }

    .hero-date {
      margin-top: 5px;
      font-size: 16.5px;
      color: #cbd5e1;
      font-weight: 400;
      text-transform: capitalize;
      letter-spacing: 0.3px;
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.8);
    }

    /* MUSIC PLAYER WIDGET (Glassmorphic) */
    .music-widget-card {
      background: rgba(11, 16, 28, 0.78);
      backdrop-filter: blur(28px);
      -webkit-backdrop-filter: blur(28px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 18px;
      padding: 10px 18px;
      display: flex;
      align-items: center;
      gap: 16px;
      width: 480px;
      box-shadow: 0 14px 34px rgba(0, 0, 0, 0.7);
      position: relative;
      overflow: hidden;
      cursor: pointer;
      transition: border-color 0.25s, transform 0.25s;
    }

    .music-widget-card:hover {
      border-color: rgba(56, 189, 248, 0.4);
      transform: translateY(-2px);
    }

    .music-artwork {
      width: 60px;
      height: 60px;
      border-radius: 12px;
      overflow: hidden;
      flex-shrink: 0;
      border: 1px solid rgba(255, 255, 255, 0.15);
      background: #0f172a;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.5);
    }

    .music-artwork img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }

    .music-info {
      flex: 1;
      min-width: 0;
    }

    .music-badge-label {
      font-size: 11px;
      color: #38bdf8;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .music-badge-label::before {
      content: '';
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #38bdf8;
      box-shadow: 0 0 8px #38bdf8;
      animation: pulseDot 2s infinite;
    }

    @keyframes pulseDot {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(0.8); }
    }

    .music-title {
      font-size: 17px;
      font-weight: 600;
      color: #ffffff;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      margin-top: 2px;
    }

    .music-artist {
      font-size: 13px;
      color: #94a3b8;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      margin-top: 1px;
    }

    .music-controls {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-shrink: 0;
    }

    .music-ctrl-btn {
      background: transparent;
      border: none;
      color: #cbd5e1;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 6px;
      border-radius: 50%;
      transition: all 0.2s;
    }

    .music-ctrl-btn:hover {
      color: #ffffff;
      transform: scale(1.12);
    }

    .music-ctrl-btn.play-circle {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      border: 1.8px solid rgba(255, 255, 255, 0.8);
      background: rgba(255, 255, 255, 0.08);
      color: #ffffff;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .music-ctrl-btn.play-circle:hover {
      background: #ffffff;
      color: #030712;
      border-color: #ffffff;
      box-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
      transform: scale(1.08);
    }

    /* CENTRAL ROW OF 6 LUXURY CARDS (Exact match to reference Image 2) */
    .bottom-cards-row {
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 10px;
      margin-bottom: 8px;
      width: 100%;
    }

    .luxury-card {
      position: relative;
      aspect-ratio: 1.25 / 1;
      border-radius: 18px;
      cursor: pointer;
      background: #080d1a;
      border: 1px solid rgba(255, 255, 255, 0.08);
      overflow: hidden;
      transition: all 0.24s cubic-bezier(0.2, 0.8, 0.2, 1);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
    }

    .luxury-card img.card-texture {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      border-radius: 17px;
      transition: transform 0.25s ease;
    }

    .luxury-card:hover {
      transform: translateY(-4px);
      border-color: rgba(56, 189, 248, 0.45);
      box-shadow: 0 12px 30px rgba(0, 0, 0, 0.7), 0 0 16px rgba(56, 189, 248, 0.25);
    }

    .luxury-card:hover img.card-texture {
      transform: scale(1.025);
    }

    .luxury-card:active {
      transform: scale(0.96);
    }

    /* CLEAN BOTTOM TEXT LABEL — NO RECUADRO ANIDADO, NO DUPLICATE ICONS */
    .card-bottom-label {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 12px 8px 9px 8px;
      background: linear-gradient(0deg, rgba(3, 7, 18, 0.95) 0%, rgba(3, 7, 18, 0.55) 60%, transparent 100%);
      text-align: center;
      font-size: 14px;
      font-weight: 600;
      color: #ffffff;
      letter-spacing: 0.3px;
      text-shadow: 0 2px 8px rgba(0, 0, 0, 0.95);
      pointer-events: none;
    }

    /* CARD 6: CLIMA CONTENT (Fan on top-left, 24°C on top-right, A/C activado, Clima at bottom) */
    .card-climate-content {
      position: absolute;
      inset: 0;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 12px 14px 9px 14px;
      pointer-events: none;
      background: linear-gradient(180deg, rgba(3, 7, 18, 0.45) 0%, rgba(3, 7, 18, 0.2) 40%, rgba(3, 7, 18, 0.92) 100%);
    }

    .climate-header-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
    }

    .climate-fan-svg {
      width: 24px;
      height: 24px;
      color: #ffffff;
      filter: drop-shadow(0 2px 6px rgba(0,0,0,0.8));
    }

    .climate-temp-val {
      font-size: 26px;
      font-weight: 700;
      color: #ffffff;
      font-family: var(--font-mono);
      letter-spacing: -0.5px;
      text-shadow: 0 2px 8px rgba(0, 0, 0, 0.95);
      line-height: 1;
    }

    .climate-status-text {
      text-align: center;
      font-size: 11px;
      color: #cbd5e1;
      font-weight: 500;
      letter-spacing: 0.2px;
      text-shadow: 0 1px 4px rgba(0, 0, 0, 0.9);
      margin-top: auto;
      margin-bottom: 2px;
    }

    /* BARRA DE FAVORITOS (Exact match to reference Image 3) */
    .favorites-bar {
      display: flex;
      align-items: center;
      gap: 10px;
      background: rgba(11, 16, 28, 0.72);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 14px;
      padding: 6px 14px;
      width: 100%;
      min-height: 48px;
      box-shadow: 0 10px 28px rgba(0, 0, 0, 0.55);
      margin-top: 0;
      margin-bottom: 6px;
      overflow-x: auto;
    }

    .favorites-bar::-webkit-scrollbar {
      display: none;
    }

    .fav-badge {
      font-size: 10.5px;
      font-weight: 700;
      color: #94a3b8;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      white-space: nowrap;
      padding: 0 2px;
      flex-shrink: 0;
    }

    .fav-divider {
      width: 1px;
      height: 20px;
      background: rgba(255, 255, 255, 0.12);
      flex-shrink: 0;
      margin: 0 2px;
    }

    .fav-chips-container {
      display: flex;
      align-items: center;
      gap: 8px;
      overflow-x: auto;
      flex-wrap: nowrap;
    }

    .fav-chips-container::-webkit-scrollbar {
      display: none;
    }

    .fav-pill-btn {
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 6px 13px;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      color: #e2e8f0;
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      flex-shrink: 0;
      text-decoration: none;
    }

    .fav-pill-btn .app-icon {
      width: 18px;
      height: 18px;
      object-fit: contain;
      flex-shrink: 0;
      color: #cbd5e1;
    }

    .fav-pill-btn:hover {
      background: rgba(255, 255, 255, 0.09);
      border-color: rgba(56, 189, 248, 0.4);
      color: #ffffff;
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
    }

    .fav-pill-btn:active {
      transform: scale(0.96);
    }

    /* PAGINATION INDICATOR (Pill + Dot) */
    .pagination-bar {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 2px 0 4px 0;
    }

    .page-indicator-pill {
      width: 24px;
      height: 4px;
      border-radius: 2px;
      background: #ffffff;
      box-shadow: 0 0 10px rgba(255, 255, 255, 0.6);
      cursor: pointer;
      transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .page-indicator-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.3);
      cursor: pointer;
      transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .page-indicator-dot:hover, .page-indicator-pill:hover {
      background: #ffffff;
    }

    /* PAGE 2: APP DRAWER */
    .page-apps {
      padding: 6px 0;
    }

    .apps-header-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }

    .apps-title-block h3 {
      font-size: 21px;
      font-weight: 700;
      color: #f8fafc;
      letter-spacing: -0.5px;
    }

    .apps-title-block p {
      font-size: 12.5px;
      color: #94a3b8;
      margin-top: 1px;
    }

    .btn-action-pill {
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #ffffff;
      border-radius: 12px;
      padding: 7px 16px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }

    .btn-action-pill:hover {
      background: rgba(56, 189, 248, 0.2);
      border-color: #38bdf8;
      color: #38bdf8;
    }

    .btn-oem-return {
      background: linear-gradient(135deg, rgba(217, 119, 6, 0.3) 0%, rgba(180, 83, 9, 0.6) 100%);
      border: 1.5px solid rgba(245, 158, 11, 0.7);
      color: #fbbf24;
      box-shadow: 0 0 16px rgba(245, 158, 11, 0.25);
    }

    .btn-oem-return:hover {
      background: linear-gradient(135deg, rgba(217, 119, 6, 0.6) 0%, rgba(180, 83, 9, 0.9) 100%);
      color: #ffffff;
      border-color: #fbbf24;
    }

    .app-drawer-grid {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 12px;
      flex: 1;
      align-content: start;
      overflow-y: auto;
      padding-right: 6px;
      max-height: 480px;
    }

    .app-drawer-grid::-webkit-scrollbar {
      width: 4px;
    }
    .app-drawer-grid::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.15);
      border-radius: 2px;
    }

    .app-tile {
      background: rgba(13, 18, 30, 0.75);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      padding: 12px 10px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      transition: all 0.22s cubic-bezier(0.2, 0.8, 0.2, 1);
      position: relative;
      overflow: hidden;
    }

    .app-tile:hover {
      background: rgba(255, 255, 255, 0.08);
      border-color: rgba(56, 189, 248, 0.45);
      transform: translateY(-3px);
      box-shadow: 0 10px 24px rgba(0, 0, 0, 0.6), 0 0 16px rgba(56, 189, 248, 0.2);
    }

    .app-tile:active {
      transform: scale(0.95);
    }

    .app-tile-icon {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #38bdf8;
      transition: all 0.22s;
    }

    .app-tile:hover .app-tile-icon {
      background: rgba(56, 189, 248, 0.18);
      border-color: #38bdf8;
      color: #ffffff;
      box-shadow: 0 0 14px rgba(56, 189, 248, 0.4);
    }

    .app-tile-icon svg {
      width: 24px;
      height: 24px;
    }

    .app-tile span {
      font-size: 13px;
      font-weight: 600;
      color: #e2e8f0;
      text-align: center;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      width: 100%;
    }

    .app-tile small {
      font-size: 10.5px;
      color: #94a3b8;
      text-align: center;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      width: 100%;
    }

    /* HUD MODAL SYSTEM */
    .hud-modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(3, 7, 18, 0.85);
      backdrop-filter: blur(25px);
      -webkit-backdrop-filter: blur(25px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 500;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.28s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .hud-modal-overlay.open {
      opacity: 1;
      pointer-events: auto;
    }

    .hud-modal-card {
      background: rgba(13, 20, 36, 0.95);
      border: 1px solid rgba(56, 189, 248, 0.35);
      border-radius: 24px;
      width: 90%;
      max-width: 640px;
      padding: 24px 28px;
      box-shadow: 0 24px 60px rgba(0, 0, 0, 0.85), 0 0 40px rgba(56, 189, 248, 0.2);
      transform: scale(0.92);
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      position: relative;
    }

    .hud-modal-overlay.open .hud-modal-card {
      transform: scale(1);
    }

    .hud-modal-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      padding-bottom: 12px;
    }

    .hud-modal-title {
      font-size: 19px;
      font-weight: 700;
      color: #ffffff;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .hud-modal-close {
      background: rgba(255, 255, 255, 0.08);
      border: none;
      color: #94a3b8;
      width: 34px;
      height: 34px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.2s;
    }

    .hud-modal-close:hover {
      background: rgba(255, 255, 255, 0.18);
      color: #ffffff;
    }

    /* TOAST FEEDBACK */
    .cockpit-toast {
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%) translateY(30px);
      background: rgba(15, 23, 42, 0.94);
      border: 1px solid rgba(56, 189, 248, 0.45);
      backdrop-filter: blur(16px);
      padding: 10px 22px;
      border-radius: 20px;
      color: #ffffff;
      font-size: 13.5px;
      font-weight: 600;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7), 0 0 20px rgba(56, 189, 248, 0.25);
      opacity: 0;
      pointer-events: none;
      transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 9999;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .cockpit-toast.show {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }
  </style>
</head>
<body>

  <div class="cockpit-container">
    
    <!-- LEFT VERTICAL DOCK (Fixed 6 Icons) -->
    <nav class="cockpit-dock" id="cockpit-dock">
      <div class="dock-items-wrapper">
        <!-- 1. INICIO (Active by default) -->
        <button class="dock-btn active" id="dock-btn-home" title="Pantalla Principal">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          <span>Inicio</span>
        </button>

        <!-- 2. NAVEGACIÓN (Click -> Waze / Magic Earth, Long-press -> Selector) -->
        <button class="dock-btn" id="dock-btn-nav" title="Navegación GPS (Mantén presionado para elegir Waze, Magic Earth o Android Auto)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg>
          <span>Navegación</span>
        </button>

        <!-- 3. MÚSICA (RiMusic) -->
        <button class="dock-btn" id="dock-btn-music" title="Música RiMusic">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
          <span>Música</span>
        </button>

        <!-- 4. TELÉFONO (Bluetooth OEM) -->
        <button class="dock-btn" id="dock-btn-phone" title="Teléfono Bluetooth Manos Libres">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
          <span>Teléfono</span>
        </button>

        <!-- 5. APPS (Drawer) -->
        <button class="dock-btn" id="dock-btn-apps" title="Cajón de Aplicaciones">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
          <span>Apps</span>
        </button>

        <!-- 6. AJUSTES (Click -> OnStyle Settings, Long-press -> Android Settings) -->
        <button class="dock-btn" id="dock-btn-settings" title="Ajustes Changan (Mantén presionado para Ajustes Ocultos Android)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
          <span>Ajustes</span>
        </button>
      </div>
    </nav>

    <!-- MAIN DASHBOARD CONTENT AREA -->
    <main class="cockpit-main">
      
      <!-- TOP STATUS BAR (Bluetooth, WiFi, 4G, Clock) -->
      <header class="cockpit-statusbar">
        <div class="status-icons">
          <!-- Bluetooth -->
          <button class="status-icon-btn" id="status-btn-bt" title="Bluetooth del Auto">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6.5 6.5 17.5 17.5 12 23 12 1 17.5 6.5 6.5 17.5"/></svg>
          </button>
          <!-- Wifi -->
          <button class="status-icon-btn" id="status-btn-wifi" title="WiFi 5G Conectado">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12.55a11 11 0 0 1 14.08 0M1.42 9a16 16 0 0 1 21.16 0M8.53 16.11a6 6 0 0 1 6.95 0M12 20h.01"/></svg>
          </button>
          <!-- Signal 4G/LTE -->
          <button class="status-icon-btn" id="status-btn-signal" title="Señal LTE Cobertura Total">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="4"/><line x1="12" y1="20" x2="12" y2="9"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="1" y1="20" x2="1" y2="18"/></svg>
          </button>
        </div>

        <span class="status-clock" id="status-top-clock">22:09</span>
      </header>

      <!-- SLIDER CONTAINER WITH ISOLATED VIEWPORT -->
      <div class="slider-viewport">
        <div class="pages-slider" id="pages-slider">
          
          <!-- PAGE 1: LUXURY COCKPIT -->
          <section class="page" id="page-cockpit">
            
            <!-- HERO (CLOCK + MUSIC WIDGET) -->
            <div class="hero-section">
              <div class="hero-clock-block">
                <div class="hero-clock" id="hero-clock">22:09</div>
                <div class="hero-date" id="hero-date">Miércoles, 14 de octubre</div>
              </div>

              <!-- MUSIC WIDGET (Glassmorphic) -->
              <div class="music-widget-card" id="music-widget" title="Toca para abrir RiMusic">
                <div class="music-artwork">
                  <img src="assets/album_art.png" alt="Album Art" id="player-art-img">
                </div>
                <div class="music-info">
                  <div class="music-badge-label">
                    <span>Reproduciendo</span>
                  </div>
                  <div class="music-title" id="player-title">RiMusic Streaming</div>
                  <div class="music-artist" id="player-artist">Changan Audio Hi-Fi</div>
                </div>
                <div class="music-controls" onclick="event.stopPropagation();">
                  <button class="music-ctrl-btn" id="btn-player-prev" title="Canción Anterior">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><polygon points="19 20 9 12 19 4 19 20"/><line x1="5" y1="19" x2="5" y2="5" stroke="currentColor" stroke-width="3"/></svg>
                  </button>
                  <button class="music-ctrl-btn play-circle" id="btn-player-playpause" title="Pausar / Reproducir">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" id="playpause-icon">
                      <rect x="6" y="4" width="3.5" height="16" rx="1.5"/>
                      <rect x="14.5" y="4" width="3.5" height="16" rx="1.5"/>
                    </svg>
                  </button>
                  <button class="music-ctrl-btn" id="btn-player-next" title="Siguiente Canción">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><polygon points="5 4 15 12 5 20 5 4"/><line x1="19" y1="5" x2="19" y2="19" stroke="currentColor" stroke-width="3"/></svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- CENTRAL ROW OF 6 LUXURY CARDS (Exact Match to Reference Image 2) -->
            <div class="bottom-cards-row">
              
              <!-- 1. NAVEGACIÓN -->
              <div class="luxury-card" id="card-nav" title="Navegación GPS (Mantén presionado para Pantalla Dividida)">
                <img class="card-texture" src="assets/card_nav.png" alt="Navegación">
                <div class="card-bottom-label">Navegación</div>
              </div>

              <!-- 2. MÚSICA -->
              <div class="luxury-card" id="card-music" title="Música RiMusic (Mantén presionado para Pantalla Dividida)">
                <img class="card-texture" src="assets/card_music.png" alt="Música">
                <div class="card-bottom-label">Música</div>
              </div>

              <!-- 3. TELÉFONO -->
              <div class="luxury-card" id="card-phone" title="Teléfono Bluetooth Manos Libres">
                <img class="card-texture" src="assets/card_phone.png" alt="Teléfono">
                <div class="card-bottom-label">Teléfono</div>
              </div>

              <!-- 4. CÁMARA 360 -->
              <div class="luxury-card" id="card-camera" title="Cámaras 360° AVM Changan">
                <img class="card-texture" src="assets/card_camera.png" alt="Cámara 360">
                <div class="card-bottom-label">Cámara 360</div>
              </div>

              <!-- 5. VEHÍCULO -->
              <div class="luxury-card" id="card-car" title="Ajustes y Control del Vehículo">
                <img class="card-texture" src="assets/card_car.png" alt="Vehículo">
                <div class="card-bottom-label">Vehículo</div>
              </div>

              <!-- 6. CLIMA -->
              <div class="luxury-card" id="card-climate" title="Climatizador A/C Changan (Abre com.os.airconditioner)">
                <img class="card-texture" src="assets/card_climate.png" alt="Clima">
                <div class="card-climate-content">
                  <div class="climate-header-row">
                    <svg class="climate-fan-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 9a3 3 0 0 0-3-3H4a1 1 0 0 0-1 1 3 3 0 0 0 3 3h6zM15 12a3 3 0 0 0 3-3V4a1 1 0 0 0-1-1 3 3 0 0 0-3 3v6zM12 15a3 3 0 0 0 3 3h5a1 1 0 0 0 1-1 3 3 0 0 0-3-3h-6zM9 12a3 3 0 0 0-3 3v5a1 1 0 0 0 1 1 3 3 0 0 0 3-3v-6z"/></svg>
                    <span class="climate-temp-val" id="card-climate-temp">24°C</span>
                  </div>
                  <div class="climate-status-text">A/C activado</div>
                  <div class="card-bottom-label" style="position:relative; background:none; padding:0;">Clima</div>
                </div>
              </div>

            </div>

            <!-- BARRA DE FAVORITOS (Exact Match to Reference Image 3) -->
            <div class="favorites-bar" id="favorites-bar">
              <span class="fav-badge">FAVORITOS</span>
              <div class="fav-divider"></div>
              <div class="fav-chips-container" id="fav-chips-container">
                <!-- 1. Radio -->
                <button class="fav-pill-btn" data-app="com.edog.car.changanoushang" data-name="Radio" title="Radio FM / AM Changan">
                  <svg class="app-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="2" y="7" width="20" height="14" rx="3"/>
                    <path d="M4.5 7L10.5 2"/>
                    <circle cx="8" cy="14" r="3"/>
                    <line x1="14" y1="12" x2="18" y2="12"/>
                    <line x1="14" y1="16" x2="18" y2="16"/>
                  </svg>
                  <span>Radio</span>
                </button>
                <!-- 2. Reproductor de música -->
                <button class="fav-pill-btn" data-app="it.fast4x.rimusic" data-name="Reproductor de música" title="Reproductor de música RiMusic">
                  <svg class="app-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M9 18V5l12-2v13"/>
                    <circle cx="6" cy="18" r="3" fill="currentColor"/>
                    <circle cx="18" cy="16" r="3" fill="currentColor"/>
                  </svg>
                  <span>Reproductor de música</span>
                </button>
                <!-- 3. Teléfono Bluetooth -->
                <button class="fav-pill-btn" data-app="com.chinatsp.phone" data-name="Teléfono Bluetooth" title="Teléfono Bluetooth Manos Libres">
                  <svg class="app-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20.01 15.38c-1.23 0-2.42-.2-3.53-.56a.977.977 0 0 0-1.01.24l-2.2 2.2a15.053 15.053 0 0 1-6.59-6.59l2.2-2.21a.96.96 0 0 0 .25-1.01A11.36 11.36 0 0 1 8.57 3.9c0-.55-.45-1-1-1H4.07c-.55 0-1 .45-1 1 0 9.39 7.63 17.02 17.02 17.02.55 0 1-.45 1-1v-3.54c-.01-.55-.46-1-1.08-1z"/>
                  </svg>
                  <span>Teléfono Bluetooth</span>
                </button>
                <!-- 4. Brave (Authentic Default App Icon) -->
                <button class="fav-pill-btn" data-app="com.brave.browser" data-name="Brave" title="Navegador Brave">
                  <img class="app-icon" src="assets/icon_brave.webp" alt="Brave" style="border-radius: 4px;">
                  <span>Brave</span>
                </button>
                <!-- 5. Agregar acceso directo (Pill side-by-side with uniform styling) -->
                <button class="fav-pill-btn" id="btn-add-fav" title="Agregar acceso directo a Favoritos">
                  <svg class="app-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                  <span>Agregar acceso directo</span>
                </button>
              </div>
            </div>

            <!-- PAGINATION PILL & DOT -->
            <div class="pagination-bar">
              <div class="page-indicator-pill" id="pill-p0" title="Página 1: Cockpit"></div>
              <div class="page-indicator-dot" id="pill-p1" title="Página 2: Aplicaciones"></div>
            </div>

          </section>

          <!-- PAGE 2: APP DRAWER -->
          <section class="page page-apps" id="page-apps">
            <div class="apps-header-row">
              <div class="apps-title-block">
                <h3>Aplicaciones Changan X7 Plus</h3>
                <p>Toca cualquier aplicación para abrirla directamente en la pantalla del vehículo.</p>
              </div>
              <div style="display:flex; gap:10px;">
                <button class="btn-action-pill btn-oem-return" id="btn-return-onstyle">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>
                  Volver a OnStyle Original
                </button>
                <button class="btn-action-pill" id="btn-back-to-cockpit">
                  ← Volver al Cockpit
                </button>
              </div>
            </div>

            <div class="app-drawer-grid">
              <!-- Android Auto (Headunit Reloaded) -->
              <div class="app-tile" data-pkg="gb.xxy.hr" data-name="Android Auto" title="Headunit Reloaded (Android Auto Nativo)">
                <div class="app-tile-icon" style="background:rgba(56, 189, 248, 0.15); border-color:#38bdf8; color:#38bdf8;">
                  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L4.5 20.29l.71.71L12 18l6.79 3 .71-.71z"/></svg>
                </div>
                <span>Android Auto</span>
                <small>Headunit Reloaded</small>
              </div>

              <!-- Waze GPS -->
              <div class="app-tile" data-pkg="com.waze" data-name="Waze GPS" title="Waze GPS y Tráfico">
                <div class="app-tile-icon" style="padding:0; overflow:hidden; border-color:rgba(56,189,248,0.3);">
                  <img src="assets/icon_waze.png" alt="Waze" style="width:100%; height:100%; object-fit:cover; border-radius:12px;">
                </div>
                <span>Waze GPS</span>
                <small>Tráfico en Vivo</small>
              </div>

              <!-- Magic Earth GPS -->
              <div class="app-tile" data-pkg="com.generalmagic.magicearth" data-name="Magic Earth" title="Magic Earth Navegación 3D">
                <div class="app-tile-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
                </div>
                <span>Magic Earth</span>
                <small>GPS Offline 3D</small>
              </div>

              <!-- RiMusic -->
              <div class="app-tile" data-pkg="it.fast4x.rimusic" data-name="RiMusic" title="RiMusic Streaming y Descargas">
                <div class="app-tile-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
                </div>
                <span>RiMusic</span>
                <small>Música Sin Anuncios</small>
              </div>

              <!-- NewPipe YouTube -->
              <div class="app-tile" data-pkg="org.schabi.newpipe" data-name="YouTube (NewPipe)" title="YouTube sin Anuncios">
                <div class="app-tile-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                </div>
                <span>YouTube / NewPipe</span>
                <small>Videos Libres</small>
              </div>

              <!-- SmartTube Pro -->
              <div class="app-tile" data-pkg="org.smarttube.stable" data-name="SmartTube Pro" title="SmartTube Automotriz">
                <div class="app-tile-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.33z"/><polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02"/></svg>
                </div>
                <span>SmartTube Pro</span>
                <small>YouTube Auto</small>
              </div>

              <!-- Brave Browser -->
              <div class="app-tile" data-pkg="com.brave.browser" data-name="Brave Browser" title="Navegador Seguro">
                <div class="app-tile-icon" style="padding:2px; overflow:hidden;">
                  <img src="assets/icon_brave.webp" alt="Brave" style="width:100%; height:100%; object-fit:contain;">
                </div>
                <span>Brave Browser</span>
                <small>Navegación Web</small>
              </div>

              <!-- XuperTV / TV Streaming -->
              <div class="app-tile" data-pkg="com.lagradost.cloudstream3" data-name="XuperTV" title="TV en Vivo y Películas">
                <div class="app-tile-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="15" rx="2" ry="2"/><polyline points="17 2 12 7 7 2"/></svg>
                </div>
                <span>XuperTV / Películas</span>
                <small>Streaming Gratis</small>
              </div>

              <!-- Organic Maps -->
              <div class="app-tile" data-pkg="app.organicmaps" data-name="Organic Maps" title="Mapas Offline Libres">
                <div class="app-tile-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 19 21 12 17 5 21 12 2"/></svg>
                </div>
                <span>Organic Maps</span>
                <small>GPS OpenStreetMap</small>
              </div>

              <!-- Amaze File Manager -->
              <div class="app-tile" data-pkg="com.amaze.filemanager" data-name="Amaze USB" title="Explorador de Archivos USB">
                <div class="app-tile-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
                </div>
                <span>Amaze USB</span>
                <small>Archivos y APKs</small>
              </div>

              <!-- Radio Original Changan -->
              <div class="app-tile" data-pkg="com.edog.car.changanoushang" data-name="Radio Original" title="Radio FM / AM Changan de Fábrica">
                <div class="app-tile-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="2"/><path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"/></svg>
                </div>
                <span>Radio Original</span>
                <small>Sintonizador OEM</small>
              </div>

              <!-- Climatizador Original Changan -->
              <div class="app-tile" data-pkg="com.os.airconditioner" data-name="Climatizador A/C" title="Climatizador Original Changan">
                <div class="app-tile-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 9a3 3 0 0 0-3-3H4a1 1 0 0 0-1 1 3 3 0 0 0 3 3h6zM15 12a3 3 0 0 0 3-3V4a1 1 0 0 0-1-1 3 3 0 0 0-3 3v6zM12 15a3 3 0 0 0 3 3h5a1 1 0 0 0 1-1 3 3 0 0 0-3-3h-6zM9 12a3 3 0 0 0-3 3v5a1 1 0 0 0 1 1 3 3 0 0 0 3-3v-6z"/></svg>
                </div>
                <span>Climatizador A/C</span>
                <small>Control OEM Changan</small>
              </div>

              <!-- Teléfono Bluetooth Original -->
              <div class="app-tile" data-pkg="com.chinatsp.phone" data-name="Teléfono Bluetooth" title="Teléfono Bluetooth Original">
                <div class="app-tile-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3"/></svg>
                </div>
                <span>Teléfono Bluetooth</span>
                <small>Manos Libres OEM</small>
              </div>

              <!-- Cámara 360 Original (AVM) -->
              <div class="app-tile" data-pkg="com.chinatsp.avmlive" data-name="Cámara 360°" title="Cámara 360° AVM Changan">
                <div class="app-tile-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2"/></svg>
                </div>
                <span>Cámara 360° AVM</span>
                <small>Visión Perimétrica OEM</small>
              </div>

              <!-- Control del Vehículo Original -->
              <div class="app-tile" data-pkg="com.chinatsp.vehiclecontrol" data-name="Control de Vehículo" title="Control del Vehículo Changan">
                <div class="app-tile-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>
                </div>
                <span>Control de Vehículo</span>
                <small>Telemetría y Ajustes</small>
              </div>

              <!-- Ajustes Originales OnStyle -->
              <div class="app-tile" data-pkg="com.chinatsp.settings" data-name="Ajustes OnStyle" title="Configuración de Fábrica OnStyle">
                <div class="app-tile-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
                </div>
                <span>Ajustes OnStyle</span>
                <small>Configuración OEM</small>
              </div>

              <!-- Ajustes Ocultos de Android -->
              <div class="app-tile" data-pkg="com.android.settings" data-name="Ajustes Android" title="Ajustes de Sistema Android Nativo">
                <div class="app-tile-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M2 12h20M4.93 4.93l14.14 14.14M4.93 19.07l14.14-14.14"/></svg>
                </div>
                <span>Ajustes Android</span>
                <small>Ajustes Ocultos / AOSP</small>
              </div>

              <!-- Taskbar Pantalla Dividida -->
              <div class="app-tile" data-pkg="com.farmerbb.taskbar" data-name="Taskbar" title="Taskbar Pantalla Dividida">
                <div class="app-tile-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="15" x2="21" y2="15"/></svg>
                </div>
                <span>Taskbar Split</span>
                <small>Pantalla Dividida</small>
              </div>

              <!-- Launcher Original OnStyle -->
              <div class="app-tile" data-pkg="com.chinatsp.launcher" data-name="OnStyle Launcher" style="border-color:rgba(245, 158, 11, 0.4);" title="Abrir Launcher Original de Fábrica">
                <div class="app-tile-icon" style="color:#fbbf24; background:rgba(245, 158, 11, 0.15); border-color:#fbbf24;">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>
                </div>
                <span>Launcher OnStyle</span>
                <small>Interfaz de Fábrica</small>
              </div>

            </div>

            <!-- PAGINATION PILL & DOT FOR PAGE 2 -->
            <div class="pagination-bar">
              <div class="page-indicator-dot" id="pill2-p0" title="Página 1: Cockpit"></div>
              <div class="page-indicator-pill" id="pill2-p1" title="Página 2: Aplicaciones"></div>
            </div>
          </section>

        </div>
      </div>
    </main>

  </div>

  <!-- MODALS SYSTEM (CHANGAN TWEAKER) -->

  <!-- 1. SELECTOR NAVEGACIÓN GPS (LONG PRESS DOCK NAV) -->
  <div class="hud-modal-overlay" id="hud-nav-select">
    <div class="hud-modal-card">
      <div class="hud-modal-header">
        <div class="hud-modal-title">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#38bdf8" stroke-width="2"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg>
          Seleccionar Navegación GPS Preferida
        </div>
        <button class="hud-modal-close" data-close="hud-nav-select">✕</button>
      </div>
      <div style="font-size:13px; color:#94a3b8; margin-bottom:16px;">Toca una aplicación para iniciarla y fijarla como navegador principal:</div>
      <div class="app-drawer-grid" style="grid-template-columns: repeat(2, 1fr); gap:14px;">
        <div class="app-tile" onclick="chooseNavApp('com.waze', 'Waze GPS')">
          <div class="app-tile-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg></div>
          <span>Waze GPS</span>
          <small>Tráfico en tiempo real y alertas</small>
        </div>
        <div class="app-tile" onclick="chooseNavApp('com.generalmagic.magicearth', 'Magic Earth')">
          <div class="app-tile-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg></div>
          <span>Magic Earth 3D</span>
          <small>Mapas satelitales y offline</small>
        </div>
        <div class="app-tile" onclick="chooseNavApp('gb.xxy.hr', 'Android Auto')">
          <div class="app-tile-icon"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L4.5 20.29l.71.71L12 18l6.79 3 .71-.71z"/></svg></div>
          <span>Android Auto (Headunit)</span>
          <small>Proyección de tu celular Android</small>
        </div>
        <div class="app-tile" onclick="chooseNavApp('app.organicmaps', 'Organic Maps')">
          <div class="app-tile-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 19 21 12 17 5 21 12 2"/></svg></div>
          <span>Organic Maps</span>
          <small>GPS 100% offline y libre</small>
        </div>
      </div>
    </div>
  </div>

  <!-- 2. PANTALLA DIVIDIDA (SPLIT-SCREEN) MODAL -->
  <div class="hud-modal-overlay" id="hud-splitscreen">
    <div class="hud-modal-card">
      <div class="hud-modal-header">
        <div class="hud-modal-title">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#38bdf8" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="12" y1="3" x2="12" y2="21"/></svg>
          Modo Pantalla Dividida (Changan Tweaker)
        </div>
        <button class="hud-modal-close" data-close="hud-splitscreen">✕</button>
      </div>
      <div style="font-size:13px; color:#94a3b8; margin-bottom:16px;">Selecciona la combinación para ejecutar 2 aplicaciones al 50% en la pantalla ultrawide (1920x720):</div>
      <div class="app-drawer-grid" style="grid-template-columns: repeat(2, 1fr); gap:14px;">
        <div class="app-tile" onclick="launchSplitPreset('com.waze', 'it.fast4x.rimusic', 'Waze + RiMusic')">
          <div class="app-tile-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg></div>
          <span>Waze + RiMusic</span>
          <small>Navegación + Música en Vivo</small>
        </div>
        <div class="app-tile" onclick="launchSplitPreset('com.generalmagic.magicearth', 'it.fast4x.rimusic', 'Magic Earth + RiMusic')">
          <div class="app-tile-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg></div>
          <span>Magic Earth + RiMusic</span>
          <small>GPS 3D + Streaming de Música</small>
        </div>
        <div class="app-tile" onclick="launchSplitPreset('com.waze', 'com.brave.browser', 'Waze + Brave')">
          <div class="app-tile-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg></div>
          <span>Waze + Navegador Brave</span>
          <small>GPS + Navegador Web con Adblock</small>
        </div>
        <div class="app-tile" onclick="launchSplitPreset('com.farmerbb.taskbar', '', 'Abrir Taskbar Multi-Ventana')">
          <div class="app-tile-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/></svg></div>
          <span>Taskbar Multiventana</span>
          <small>Organizador libre de ventanas</small>
        </div>
      </div>
    </div>
  </div>

  <!-- 3. AGREGAR FAVORITO MODAL -->
  <div class="hud-modal-overlay" id="hud-add-fav">
    <div class="hud-modal-card">
      <div class="hud-modal-header">
        <div class="hud-modal-title">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#38bdf8" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Personalizar Barra de Favoritos
        </div>
        <button class="hud-modal-close" data-close="hud-add-fav">✕</button>
      </div>
      <div style="font-size:13px; color:#94a3b8; margin-bottom:16px;">Toca una aplicación para agregarla como acceso rápido a la barra inferior:</div>
      <div class="app-drawer-grid" style="max-height:280px;">
        <div class="app-tile" onclick="addCustomFav('gb.xxy.hr', 'Android Auto', 'aa')">
          <div class="app-tile-icon"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L4.5 20.29l.71.71L12 18l6.79 3 .71-.71z"/></svg></div>
          <span>Android Auto</span>
          <small>+ Fijar en Barra</small>
        </div>
        <div class="app-tile" onclick="addCustomFav('com.waze', 'Waze GPS', 'waze')">
          <div class="app-tile-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg></div>
          <span>Waze GPS</span>
          <small>+ Fijar en Barra</small>
        </div>
        <div class="app-tile" onclick="addCustomFav('com.generalmagic.magicearth', 'Magic Earth', 'globe')">
          <div class="app-tile-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg></div>
          <span>Magic Earth</span>
          <small>+ Fijar en Barra</small>
        </div>
        <div class="app-tile" onclick="addCustomFav('org.schabi.newpipe', 'NewPipe', 'video')">
          <div class="app-tile-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg></div>
          <span>NewPipe</span>
          <small>+ Fijar en Barra</small>
        </div>
        <div class="app-tile" onclick="addCustomFav('org.smarttube.stable', 'SmartTube Pro', 'tv')">
          <div class="app-tile-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.33z"/><polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02"/></svg></div>
          <span>SmartTube Pro</span>
          <small>+ Fijar en Barra</small>
        </div>
        <div class="app-tile" onclick="addCustomFav('com.chinatsp.launcher', 'Menú Changan', 'oem')">
          <div class="app-tile-icon" style="color:#fbbf24;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg></div>
          <span>Menú Changan</span>
          <small>+ Fijar en Barra</small>
        </div>
      </div>
    </div>
  </div>

  <!-- TOAST FEEDBACK -->
  <div class="cockpit-toast" id="cockpit-toast">
    <span id="cockpit-toast-text">Acción ejecutada</span>
  </div>

  <script>
    // AUDIO CLICK SYNTHESIS (Acoustic tactile feedback)
    let audioCtx = null;
    function playClickSound() {
      try {
        if (!audioCtx) {
          audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioCtx.state === 'suspended') {
          audioCtx.resume();
        }
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(850, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(420, audioCtx.currentTime + 0.04);
        gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.04);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.04);
      } catch (e) {}
    }

    // TOAST SYSTEM
    function triggerToast(text) {
      const toast = document.getElementById("cockpit-toast");
      const msg = document.getElementById("cockpit-toast-text");
      if (!toast || !msg) return;
      msg.textContent = text;
      toast.classList.add("show");
      clearTimeout(window.__toastTimeout);
      window.__toastTimeout = setTimeout(() => {
        toast.classList.remove("show");
      }, 2600);
    }

    // MODAL CONTROLLER
    function openModal(id) {
      playClickSound();
      document.querySelectorAll(".hud-modal-overlay").forEach(m => m.classList.remove("open"));
      const m = document.getElementById(id);
      if (m) m.classList.add("open");
    }

    function closeModal(id) {
      playClickSound();
      const m = document.getElementById(id);
      if (m) m.classList.remove("open");
    }

    document.querySelectorAll("[data-close]").forEach(btn => {
      btn.addEventListener("click", () => {
        closeModal(btn.getAttribute("data-close"));
      });
    });

    document.querySelectorAll(".hud-modal-overlay").forEach(overlay => {
      overlay.addEventListener("click", (e) => {
        if (e.target === overlay) {
          overlay.classList.remove("open");
        }
      });
    });

    // LIVE SYNCHRONIZED CLOCK & SPANISH DATE
    function updateClock() {
      const now = new Date();
      const hours = String(now.getHours()).padStart(2, '0');
      const mins = String(now.getMinutes()).padStart(2, '0');
      const timeStr = `${hours}:${mins}`;

      const topClock = document.getElementById("status-top-clock");
      const heroClock = document.getElementById("hero-clock");
      if (topClock) topClock.textContent = timeStr;
      if (heroClock) heroClock.textContent = timeStr;

      const days = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
      const months = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
      const dayName = days[now.getDay()];
      const dayNum = String(now.getDate()).padStart(2, '0');
      const monthName = months[now.getMonth()];
      
      const dateEl = document.getElementById("hero-date");
      if (dateEl) {
        dateEl.textContent = `${dayName}, ${dayNum} de ${monthName}`;
      }
    }
    updateClock();
    setInterval(updateClock, 1000);

    // SLIDER & PAGE SWITCHING
    let currentPage = 0;
    const slider = document.getElementById("pages-slider");
    const dockHome = document.getElementById("dock-btn-home");
    const dockApps = document.getElementById("dock-btn-apps");

    function setPage(p) {
      currentPage = p;
      playClickSound();
      slider.style.transform = `translateX(-${currentPage * 50}%)`;

      if (currentPage === 0) {
        dockHome?.classList.add("active");
        dockApps?.classList.remove("active");
      } else {
        dockHome?.classList.remove("active");
        dockApps?.classList.add("active");
      }
    }

    document.getElementById("pill-p0")?.addEventListener("click", () => setPage(0));
    document.getElementById("pill-p1")?.addEventListener("click", () => setPage(1));
    document.getElementById("pill2-p0")?.addEventListener("click", () => setPage(0));
    document.getElementById("pill2-p1")?.addEventListener("click", () => setPage(1));
    dockHome?.addEventListener("click", () => setPage(0));
    dockApps?.addEventListener("click", () => setPage(1));
    document.getElementById("btn-back-to-cockpit")?.addEventListener("click", () => setPage(0));

    // KEYBOARD NAVIGATION
    window.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") setPage(1);
      if (e.key === "ArrowLeft") setPage(0);
      if (e.code === "Space") {
        e.preventDefault();
        togglePlayPause();
      }
    });

    // TOUCH SWIPE NAVIGATION
    let touchStartX = 0;
    window.addEventListener("touchstart", (e) => {
      touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    window.addEventListener("touchend", (e) => {
      const diff = e.changedTouches[0].screenX - touchStartX;
      if (diff < -70) setPage(1);
      if (diff > 70) setPage(0);
    }, { passive: true });

    // ANDROID HOST & SAFE INTENT EXECUTION
    async function launchApp(pkg, appName) {
      playClickSound();
      triggerToast(`Iniciando ${appName}...`);
      if (window.AndroidHost && typeof window.AndroidHost.launchApp === 'function') {
        try {
          window.AndroidHost.launchApp(pkg, appName);
          return;
        } catch (e) {
          console.warn("AndroidHost error:", e);
        }
      }
      try {
        await fetch('/api/adb_command', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ command: `shell monkey -p ${pkg} -c android.intent.category.LAUNCHER 1` })
        });
      } catch (err) {}
    }

    // LONG PRESS HELPER
    function attachLongPress(element, onClick, onLongPress) {
      if (!element) return;
      let timer = null;
      let isLong = false;

      function startPress(e) {
        isLong = false;
        timer = setTimeout(() => {
          isLong = true;
          playClickSound();
          onLongPress(e);
        }, 550);
      }

      function cancelPress() {
        if (timer) clearTimeout(timer);
      }

      element.addEventListener("mousedown", startPress);
      element.addEventListener("mouseup", (e) => {
        cancelPress();
        if (!isLong) onClick(e);
      });
      element.addEventListener("mouseleave", cancelPress);

      element.addEventListener("touchstart", startPress, { passive: true });
      element.addEventListener("touchend", (e) => {
        cancelPress();
        if (!isLong) onClick(e);
      });
      element.addEventListener("touchcancel", cancelPress);
    }

    // PREFERRED NAVIGATION APP
    let preferredNav = localStorage.getItem("preferred_nav_pkg") || "com.waze";
    let preferredNavName = localStorage.getItem("preferred_nav_name") || "Waze GPS";

    window.chooseNavApp = function(pkg, name) {
      preferredNav = pkg;
      preferredNavName = name;
      localStorage.setItem("preferred_nav_pkg", pkg);
      localStorage.setItem("preferred_nav_name", name);
      closeModal("hud-nav-select");
      triggerToast(`Navegación predeterminada: ${name}`);
      launchApp(pkg, name);
    };

    // DOCK NAVIGATION BINDINGS
    attachLongPress(
      document.getElementById("dock-btn-nav"),
      () => launchApp(preferredNav, preferredNavName),
      () => openModal("hud-nav-select")
    );

    // DOCK MUSIC
    document.getElementById("dock-btn-music")?.addEventListener("click", () => {
      launchApp("it.fast4x.rimusic", "RiMusic");
    });

    // DOCK PHONE (OEM com.chinatsp.phone)
    document.getElementById("dock-btn-phone")?.addEventListener("click", () => {
      launchApp("com.chinatsp.phone", "Teléfono Bluetooth");
    });

    // DOCK SETTINGS (Click -> OEM com.chinatsp.settings, Long-press -> Android AOSP com.android.settings)
    attachLongPress(
      document.getElementById("dock-btn-settings"),
      () => launchApp("com.chinatsp.settings", "Ajustes OnStyle"),
      () => {
        triggerToast("Abriendo Ajustes Ocultos de Android...");
        launchApp("com.android.settings", "Ajustes del Sistema Android");
      }
    );

    // CENTRAL 6 CARDS BINDINGS
    // Card 1: Navegación (Click -> Launch Nav, Long-press -> Split-screen)
    attachLongPress(
      document.getElementById("card-nav"),
      () => launchApp(preferredNav, preferredNavName),
      () => openModal("hud-splitscreen")
    );

    // Card 2: Música (Click -> RiMusic, Long-press -> Split-screen)
    attachLongPress(
      document.getElementById("card-music"),
      () => launchApp("it.fast4x.rimusic", "RiMusic"),
      () => openModal("hud-splitscreen")
    );

    // Card 3: Teléfono (Click -> com.chinatsp.phone)
    document.getElementById("card-phone")?.addEventListener("click", () => {
      launchApp("com.chinatsp.phone", "Teléfono Bluetooth");
    });

    // Card 4: Cámara 360 (Click -> com.chinatsp.avmlive / dvrcamera)
    document.getElementById("card-camera")?.addEventListener("click", () => {
      launchApp("com.chinatsp.avmlive", "Cámara 360° AVM");
    });

    // Card 5: Vehículo (Click -> com.chinatsp.vehiclecontrol)
    document.getElementById("card-car")?.addEventListener("click", () => {
      launchApp("com.chinatsp.vehiclecontrol", "Control del Vehículo");
    });

    // Card 6: Clima (Click -> Inmediatamente com.os.airconditioner)
    document.getElementById("card-climate")?.addEventListener("click", () => {
      triggerToast("Abriendo Climatizador A/C Changan...");
      launchApp("com.os.airconditioner", "Climatizador Changan A/C");
    });

    // MUSIC WIDGET CONTROLS
    let isPlaying = true;
    function togglePlayPause() {
      isPlaying = !isPlaying;
      playClickSound();
      const icon = document.getElementById("playpause-icon");
      if (isPlaying) {
        icon.innerHTML = `<rect x="6" y="4" width="3.5" height="16" rx="1.5"/><rect x="14.5" y="4" width="3.5" height="16" rx="1.5"/>`;
        triggerToast("Reproduciendo");
      } else {
        icon.innerHTML = `<polygon points="7 4 19 12 7 20 7 4"/>`;
        triggerToast("Pausado");
      }
      sendMediaKey(85);
    }

    function sendMediaKey(keyCode) {
      if (window.AndroidHost && typeof window.AndroidHost.sendMediaKey === 'function') {
        try { window.AndroidHost.sendMediaKey(keyCode); return; } catch (e) {}
      }
      try {
        fetch('/api/adb_command', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ command: `shell input keyevent ${keyCode}` })
        });
      } catch (err) {}
    }

    document.getElementById("btn-player-playpause")?.addEventListener("click", togglePlayPause);
    document.getElementById("btn-player-prev")?.addEventListener("click", () => {
      playClickSound();
      triggerToast("Canción anterior");
      sendMediaKey(88);
    });
    document.getElementById("btn-player-next")?.addEventListener("click", () => {
      playClickSound();
      triggerToast("Siguiente canción");
      sendMediaKey(87);
    });
    document.getElementById("music-widget")?.addEventListener("click", () => {
      launchApp("it.fast4x.rimusic", "RiMusic");
    });

    // SPLIT SCREEN PRESETS
    window.launchSplitPreset = async function(pkg1, pkg2, name) {
      closeModal("hud-splitscreen");
      playClickSound();
      triggerToast(`Iniciando ${name} en Pantalla Dividida...`);
      if (pkg1) await launchApp(pkg1, name);
      if (pkg2) {
        setTimeout(() => {
          launchApp(pkg2, name);
        }, 1200);
      }
    };

    // FAVORITES BAR CONTROLLER
    document.getElementById("btn-add-fav")?.addEventListener("click", () => {
      openModal("hud-add-fav");
    });

    document.querySelectorAll(".fav-pill-btn[data-app]").forEach(btn => {
      btn.addEventListener("click", () => {
        const pkg = btn.getAttribute("data-app");
        const name = btn.getAttribute("data-name") || "App";
        launchApp(pkg, name);
      });
    });

    const iconSvgs = {
      aa: `<svg class="app-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L4.5 20.29l.71.71L12 18l6.79 3 .71-.71z"/></svg>`,
      waze: `<svg class="app-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg>`,
      globe: `<svg class="app-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg>`,
      video: `<svg class="app-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>`,
      tv: `<svg class="app-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="15" rx="2"/></svg>`,
      oem: `<svg class="app-icon" style="color:#fbbf24;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"/></svg>`,
      default: `<svg class="app-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg>`
    };

    window.addCustomFav = function(pkg, name, iconType) {
      playClickSound();
      const container = document.getElementById("fav-chips-container");
      const addBtn = document.getElementById("btn-add-fav");
      const btn = document.createElement("button");
      btn.className = "fav-pill-btn";
      btn.setAttribute("data-app", pkg);
      btn.setAttribute("data-name", name);
      const iconMarkup = iconSvgs[iconType] || iconSvgs.default;
      btn.innerHTML = `${iconMarkup}<span>${name}</span>`;
      btn.addEventListener("click", () => launchApp(pkg, name));
      if (addBtn && addBtn.parentNode === container) {
        container.insertBefore(btn, addBtn);
      } else {
        container.appendChild(btn);
      }
      closeModal("hud-add-fav");
      triggerToast(`Fijado ${name} en Favoritos`);
      saveCustomFavorites();
    };

    function saveCustomFavorites() {
      const favs = [];
      document.querySelectorAll("#fav-chips-container .fav-pill-btn[data-app]").forEach(btn => {
        favs.push({
          pkg: btn.getAttribute("data-app"),
          name: btn.getAttribute("data-name") || btn.innerText.trim(),
          html: btn.innerHTML
        });
      });
      localStorage.setItem("changan_custom_favs", JSON.stringify(favs));
    }

    function loadCustomFavorites() {
      const saved = localStorage.getItem("changan_custom_favs");
      if (!saved) return;
      try {
        const favs = JSON.parse(saved);
        if (Array.isArray(favs) && favs.length > 4) {
          const container = document.getElementById("fav-chips-container");
          const addBtn = document.getElementById("btn-add-fav");
          for (let i = 4; i < favs.length; i++) {
            const item = favs[i];
            const btn = document.createElement("button");
            btn.className = "fav-pill-btn";
            btn.setAttribute("data-app", item.pkg);
            btn.setAttribute("data-name", item.name);
            btn.innerHTML = item.html || `<span>${item.name}</span>`;
            btn.addEventListener("click", () => launchApp(item.pkg, item.name));
            if (addBtn && addBtn.parentNode === container) {
              container.insertBefore(btn, addBtn);
            } else {
              container.appendChild(btn);
            }
          }
        }
      } catch (e) {}
    }
    loadCustomFavorites();

    // APP TILES IN APP DRAWER
    document.querySelectorAll(".app-tile[data-pkg]").forEach(tile => {
      tile.addEventListener("click", () => {
        const pkg = tile.getAttribute("data-pkg");
        const name = tile.getAttribute("data-name") || tile.querySelector("span")?.textContent || "App";
        launchApp(pkg, name);
      });
    });

    // VOLVER A ONSTYLE ORIGINAL BUTTON
    document.getElementById("btn-return-onstyle")?.addEventListener("click", () => {
      playClickSound();
      triggerToast("Volviendo a interfaz de fábrica Changan OnStyle...");
      launchApp("com.chinatsp.launcher", "Launcher OnStyle de Fábrica");
    });

    // STATUS BAR QUICK ACTIONS
    document.getElementById("status-btn-bt")?.addEventListener("click", () => {
      triggerToast("Bluetooth Changan Activo (MTK8666)");
      launchApp("com.chinatsp.phone", "Bluetooth OEM");
    });
    document.getElementById("status-btn-wifi")?.addEventListener("click", () => {
      triggerToast("WiFi Conectado");
      launchApp("com.chinatsp.settings", "Ajustes de Red");
    });
    document.getElementById("status-btn-signal")?.addEventListener("click", () => {
      triggerToast("Red 4G/LTE Vehicular Activa");
    });
  </script>
</body>
</html>
'''

# Write to both locations
destinations = [
    os.path.join("launcher_web", "cockpit.html"),
    os.path.join("launcher_android", "assets", "cockpit.html"),
    os.path.join("launcher_android", "assets", "index.html")
]

for d in destinations:
    os.makedirs(os.path.dirname(d), exist_ok=True)
    with open(d, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated Cockpit HMI: {d} ({len(html_content)} bytes)")
